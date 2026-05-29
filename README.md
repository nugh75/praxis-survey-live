# PRAXIS Survey Live

Follow-up del progetto **CNR-articolo-quantitativo** (*AI in Education*, framework PRAXIS).
Questionario online bilingue (IT/EN) con analisi delle risposte **in tempo reale**.

- **Frontend**: React + Vite + TypeScript + Recharts
- **Backend**: Python FastAPI (async) + WebSocket
- **DB**: PostgreSQL
- **Strumento**: replica esatta dei questionari originali (studenti + insegnanti, 26 domande) per confronto longitudinale con il dataset 2024.

## Architettura

```
frontend/  React SPA: compilazione questionario + dashboard live
backend/   FastAPI: API REST + WebSocket per push statistiche
  app/questions.py   definizione bilingue domande + tag PRAXIS (P/R/A/X/I/S)
  app/models.py      Response -> N Answer (value_num | value_text)
  app/analysis.py    aggregati live (medie Likert, medie PRAXIS, distribuzioni)
db/        (vuota; il volume Postgres vive in docker)
analysis/  (script di analisi offline / export — da popolare)
```

Le chiavi domanda (`Comp_Pratica`, `Fiducia_Integrazione`, ...) coincidono con
`analisi_praxis_python/question_mapping.py` del progetto articolo, quindi i dati
sono direttamente comparabili.

## Avvio rapido (Docker)

```bash
cp .env.example .env
docker compose up --build
```

- Questionario: http://localhost:5173
- Dashboard live: http://localhost:5173/dashboard/studenti
- API docs (Swagger): http://localhost:8000/docs

## Sviluppo locale (senza Docker)

**Backend** (serve un PostgreSQL in ascolto):
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="postgresql+asyncpg://praxis:praxis@localhost:5432/praxis_survey"
uvicorn app.main:app --reload
```

**Frontend**:
```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env.local
npm run dev
```

## API principali

| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| GET  | `/api/questionnaires` | elenco questionari |
| GET  | `/api/questionnaire/{id}` | domande bilingui (`studenti`/`insegnanti`) |
| POST | `/api/responses` | invia una compilazione |
| GET  | `/api/stats/{id}` | statistiche aggregate (snapshot) |
| WS   | `/ws/stats/{id}` | push statistiche a ogni nuova risposta |

## Tempo reale

Alla `POST /api/responses`, il backend ricalcola le statistiche e le invia via
WebSocket a tutte le dashboard collegate a quel questionario. Nessun polling.

## Aggiungere / modificare domande

Edita `backend/app/questions.py`. Ogni item ha: `key`, `dimension` (PRAXIS),
`type`, `label.{it,en}`, eventuali `anchors`/`options`. Il frontend si adatta
automaticamente (le domande arrivano dall'API).

## TODO

- [ ] Export CSV/XLSX in formato compatibile con `analisi_praxis_python`
- [ ] Filtro dashboard per coorte / fascia eta'
- [ ] Confronto side-by-side con baseline 2024
- [ ] Autenticazione per la dashboard
