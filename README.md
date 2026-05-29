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

## Avvio con Docker (consigliato)

### Prerequisiti

- **Docker** ≥ 24 e **Docker Compose v2** (`docker compose`, non `docker-compose`).
  Verifica: `docker --version && docker compose version`
- Porte libere sull'host: **5173** (frontend), **8000** (backend), **5432** (Postgres).

### 1. Configura le variabili

```bash
cd praxis-survey-live
cp .env.example .env
```

`.env` di default va bene per uso locale. Per esporre l'app fuori da `localhost`
modifica `VITE_API_URL` (vedi sezione "Deploy su un server").

### 2. Avvia

```bash
docker compose up --build
```

Primo avvio: scarica le immagini e fa il build (qualche minuto). I tre servizi
partono in ordine: `db` → (healthcheck) → `backend` → `frontend`. Le tabelle del
DB vengono create automaticamente al primo avvio del backend.

Quando vedi i log fermi e nessun errore, apri:

| Cosa | URL |
|------|-----|
| Questionario studenti | http://localhost:5173/survey/studenti |
| Questionario insegnanti | http://localhost:5173/survey/insegnanti |
| Dashboard live studenti | http://localhost:5173/dashboard/studenti |
| Dashboard live insegnanti | http://localhost:5173/dashboard/insegnanti |
| Home (scelta) | http://localhost:5173 |
| API docs (Swagger) | http://localhost:8000/docs |
| Health check | http://localhost:8000/api/health |

### 3. Avvio in background (detached)

```bash
docker compose up --build -d     # parte e libera il terminale
docker compose logs -f           # segui i log
docker compose logs -f backend   # solo il backend
```

### Comandi utili

```bash
docker compose ps                # stato dei container
docker compose stop              # ferma senza cancellare nulla
docker compose start             # riavvia ciò che era fermo
docker compose down              # ferma e rimuove i container (DATI SALVI nel volume)
docker compose down -v           # ATTENZIONE: rimuove anche il DB (azzera le risposte)
docker compose up --build        # rebuild dopo modifiche al codice
docker compose restart backend   # riavvia solo un servizio
```

### Verifica rapida che funzioni (live)

1. Apri la dashboard: http://localhost:5173/dashboard/studenti (mostra "0 risposte", pallino verde "live").
2. In un'altra scheda compila il questionario: http://localhost:5173/survey/studenti → **Invia**.
3. Torna alla dashboard: il contatore e i grafici si aggiornano **da soli** (WebSocket, senza ricaricare).

### Reset del database (cancella tutte le risposte)

```bash
docker compose down -v && docker compose up --build -d
```

### Backup / export dei dati

```bash
# dump SQL completo
docker compose exec db pg_dump -U praxis praxis_survey > backup_$(date +%F).sql

# export risposte in CSV (esempio: tabella answers)
docker compose exec db psql -U praxis praxis_survey -c "\copy (SELECT * FROM answers) TO STDOUT WITH CSV HEADER" > answers.csv
```

### Deploy su un server (accesso da altri dispositivi)

Il frontend è compilato con l'URL del backend a **build-time** (`VITE_API_URL`).
Per usarlo fuori da `localhost`:

1. In `.env` imposta `VITE_API_URL=http://IP_O_DOMINIO:8000` e `CORS_ORIGINS` col dominio del frontend.
2. In `docker-compose.yml` cambia l'`args: VITE_API_URL` del servizio `frontend` (o passalo via env).
3. Rebuild: `docker compose up --build -d`.
4. Per HTTPS metti un reverse proxy (Caddy / Nginx / Traefik) davanti a `5173` e `8000`;
   con HTTPS il frontend userà automaticamente `wss://` per il WebSocket.

### Troubleshooting

| Sintomo | Causa / fix |
|---------|-------------|
| `port is already allocated` | Porta occupata. Cambia il mapping in `docker-compose.yml` (es. `"5174:80"`) o libera la porta. |
| Backend riparte in loop | DB non pronto: l'healthcheck lo gestisce, ma controlla `docker compose logs db`. |
| Dashboard resta "In attesa di risposte" | Backend irraggiungibile o `VITE_API_URL` errato. Verifica http://localhost:8000/api/health. |
| Grafici non si aggiornano live | WebSocket bloccato (proxy/firewall). In locale non dovrebbe capitare. |
| Modifiche al codice non appaiono | Serve rebuild: `docker compose up --build`. |
| Errori CORS nel browser | Aggiungi l'origine del frontend a `CORS_ORIGINS` in `.env` e rifai `up`. |

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
