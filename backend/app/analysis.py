"""Statistiche live per la dashboard (medie Likert, conteggi, ore)."""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Answer, Response
from .questions import DIMENSIONS, QUESTIONNAIRES, question_index


async def compute_stats(session: AsyncSession, questionnaire: str) -> dict:
    qidx = question_index(questionnaire)
    if not qidx:
        return {"error": "unknown questionnaire"}

    total = await session.scalar(
        select(func.count(Response.id)).where(Response.questionnaire == questionnaire)
    )

    # Aggregati numerici per item (likert + number): media, n, min, max
    rows = (
        await session.execute(
            select(
                Answer.question_key,
                Answer.dimension,
                func.count(Answer.value_num),
                func.avg(Answer.value_num),
                func.min(Answer.value_num),
                func.max(Answer.value_num),
            )
            .join(Response, Response.id == Answer.response_id)
            .where(Response.questionnaire == questionnaire, Answer.value_num.isnot(None))
            .group_by(Answer.question_key, Answer.dimension)
        )
    ).all()

    items = {}
    for key, dim, n, avg, mn, mx in rows:
        q = qidx.get(key, {})
        items[key] = {
            "key": key,
            "dimension": dim,
            "type": q.get("type"),
            "label": q.get("label"),
            "n": int(n or 0),
            "mean": round(float(avg), 2) if avg is not None else None,
            "min": mn,
            "max": mx,
        }

    # Distribuzione risposte categoriche (single / boolean): conteggio per valore
    cat_rows = (
        await session.execute(
            select(
                Answer.question_key,
                Answer.value_text,
                func.count(Answer.id),
            )
            .join(Response, Response.id == Answer.response_id)
            .where(Response.questionnaire == questionnaire, Answer.value_text.isnot(None))
            .group_by(Answer.question_key, Answer.value_text)
        )
    ).all()

    categorical = {}
    for key, val, cnt in cat_rows:
        q = qidx.get(key, {})
        if q.get("type") not in ("single", "boolean"):
            continue
        categorical.setdefault(key, {
            "key": key, "dimension": q.get("dimension"),
            "label": q.get("label"), "type": q.get("type"), "counts": {},
        })
        categorical[key]["counts"][val] = int(cnt)

    # Medie per dimensione PRAXIS (solo item likert)
    dim_means = {}
    for it in items.values():
        if it["type"] == "likert" and it["mean"] is not None:
            dim_means.setdefault(it["dimension"], []).append(it["mean"])
    praxis = [
        {
            "dimension": d,
            "label": DIMENSIONS.get(d, {}),
            "mean": round(sum(v) / len(v), 2),
            "n_items": len(v),
        }
        for d, v in dim_means.items()
    ]
    praxis.sort(key=lambda x: x["dimension"])

    return {
        "questionnaire": questionnaire,
        "title": QUESTIONNAIRES[questionnaire]["title"],
        "total_responses": int(total or 0),
        "praxis_means": praxis,
        "items": list(items.values()),
        "categorical": list(categorical.values()),
    }
