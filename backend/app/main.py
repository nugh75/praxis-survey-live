"""FastAPI app: serve i questionari, raccoglie risposte, dashboard live via WebSocket."""
import asyncio
import os

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from .analysis import compute_stats
from .database import SessionLocal, get_session, init_db
from .models import Answer, Response
from .questions import QUESTIONNAIRES, get_questionnaire, question_index
from .schemas import ResponseIn, ResponseOut

app = FastAPI(title="PRAXIS Survey Live", version="0.1.0")

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- WebSocket hub: notifica le dashboard a ogni nuova risposta -----------
class Hub:
    def __init__(self):
        self.clients: dict[str, set[WebSocket]] = {}

    async def connect(self, ws: WebSocket, q: str):
        await ws.accept()
        self.clients.setdefault(q, set()).add(ws)

    def disconnect(self, ws: WebSocket, q: str):
        self.clients.get(q, set()).discard(ws)

    async def broadcast(self, q: str, payload: dict):
        dead = []
        for ws in list(self.clients.get(q, set())):
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, q)


hub = Hub()


@app.on_event("startup")
async def _startup():
    await init_db()


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/questionnaires")
async def list_questionnaires():
    return [
        {"id": q["id"], "title": q["title"], "n_questions": len(q["questions"])}
        for q in QUESTIONNAIRES.values()
    ]


@app.get("/api/questionnaire/{qid}")
async def get_q(qid: str):
    q = get_questionnaire(qid)
    if not q:
        raise HTTPException(404, "questionnaire not found")
    return q


@app.post("/api/responses", response_model=ResponseOut)
async def submit(payload: ResponseIn, session: AsyncSession = Depends(get_session)):
    qidx = question_index(payload.questionnaire)
    if not qidx:
        raise HTTPException(404, "questionnaire not found")

    resp = Response(questionnaire=payload.questionnaire, lang=payload.lang)
    for a in payload.answers:
        meta = qidx.get(a.question_key)
        if not meta or a.value is None or a.value == "":
            continue
        ans = Answer(question_key=a.question_key, dimension=meta["dimension"])
        if meta["type"] in ("likert", "number"):
            try:
                ans.value_num = float(a.value)
            except (TypeError, ValueError):
                continue
        else:
            ans.value_text = str(a.value)
        resp.answers.append(ans)

    if not resp.answers:
        raise HTTPException(400, "no valid answers")

    session.add(resp)
    await session.commit()
    await session.refresh(resp)

    # Notifica le dashboard collegate (in background, non blocca la risposta)
    asyncio.create_task(_push_stats(payload.questionnaire))

    return ResponseOut(
        id=resp.id, questionnaire=resp.questionnaire,
        submitted_at=resp.submitted_at.isoformat(),
    )


async def _push_stats(qid: str):
    async with SessionLocal() as s:
        stats = await compute_stats(s, qid)
    await hub.broadcast(qid, stats)


@app.get("/api/stats/{qid}")
async def stats(qid: str, session: AsyncSession = Depends(get_session)):
    if not get_questionnaire(qid):
        raise HTTPException(404, "questionnaire not found")
    return await compute_stats(session, qid)


@app.websocket("/ws/stats/{qid}")
async def ws_stats(ws: WebSocket, qid: str):
    await hub.connect(ws, qid)
    try:
        # snapshot iniziale
        async with SessionLocal() as s:
            await ws.send_json(await compute_stats(s, qid))
        while True:
            await ws.receive_text()  # keepalive (ignora contenuto)
    except WebSocketDisconnect:
        hub.disconnect(ws, qid)
    except Exception:
        hub.disconnect(ws, qid)
