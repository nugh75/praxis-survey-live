# CONTEXT — praxis-survey-live

<!-- ai4educ:context-template v1.0 -->

## Quick Reference
- **Stack**: React (TypeScript, Vite), FastAPI, PostgreSQL, Docker
- **Entry point**: `docker compose up --build -d` (frontend: 5173, backend: 8002)
- **Test**: manuale

## Domain
Questionario online bilingue (IT/EN) per il follow-up del progetto CNR-articolo-quantitativo. Analisi delle risposte in tempo reale con dashboard e WebSocket.

### Key Directories
- `frontend/` — React + Vite + TypeScript
- `backend/` — FastAPI
- `docker-compose.yml` — stack completo
