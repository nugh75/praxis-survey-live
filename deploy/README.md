# Deploy: separazione rispondenti / amministrazione

Due aree, **stesso hostname** `praxis.ai4educ.org`, separate per path:

| Area          | Path                         | Accesso                          |
|---------------|------------------------------|----------------------------------|
| Rispondenti   | `/`, `/survey/*`, `/api/`    | Pubblico (anonimo)               |
| Amministraz.  | `/admin`, `/api/stats`, `/ws/stats` | Protetto ai4auth, gruppo `admins` |

Doppia protezione:
1. **nginx** `auth_request` sulle location admin (redirect a login se anonimo).
2. **backend** ([backend/app/auth.py](../backend/app/auth.py)): si fida degli header
   `Remote-*` SOLO se firmati col segreto condiviso (`X-Forwarded-Auth-Secret`
   == `FORWARD_AUTH_SHARED_SECRET`); **altrimenti** valida il Cookie direttamente
   presso ai4auth `/api/verify`. Cosi' il login funziona anche col solo cookie
   di dominio `.ai4educ.org`, e l'header `/api/auth/me` alimenta il bottone di
   login nell'interfaccia ([frontend/src/auth.ts](../frontend/src/auth.ts)).

I rispondenti anonimi non passano mai da ai4auth.

## 1. Build frontend per produzione

Il frontend deve usare path **relativi** (same-origin) cosi' i cookie di
sessione ai4auth viaggiano sulle rotte protette. In build di produzione lasciare
`VITE_API_URL` **vuoto**:

```bash
# docker-compose.yml -> frontend.build.args
VITE_API_URL: ""
```

(In sviluppo locale resta `http://localhost:8002`.)

## 2. Vhost host nginx

Copiare [nginx-praxis.ai4educ.org.conf](nginx-praxis.ai4educ.org.conf) in
`/etc/nginx/sites-available/`, abilitarlo, `nginx -t && systemctl reload nginx`.

Upstream attesi: frontend `127.0.0.1:5173`, backend `127.0.0.1:8002`
(porte di [docker-compose.yml](../docker-compose.yml)), ai4auth `127.0.0.1:9091`.

**Segreto condiviso**: sostituire `SOSTITUIRE_CON_SEGRETO_LUNGO` nel vhost con lo
stesso valore di `FORWARD_AUTH_SHARED_SECRET` del backend (`.env`). Genera:
`openssl rand -hex 32`.

> Questo vhost e' **manuale**: usa auth selettiva per-path, non whole-host.
> NON deve essere rigenerato da `regenerateForwardAuthVhosts` del console
> (vedi punto 3, flag `manualVhost`).

## 3. ai4auth / console (repo `ai4educ-console`)

In `authelia/access_matrix.json` aggiungere il servizio con il flag che lo
esclude dalla rigenerazione automatica del vhost:

```json
{
  "hostname": "praxis.ai4educ.org",
  "label": "PRAXIS Survey (admin)",
  "groups": ["admins"],
  "manualVhost": true,
  "path": "/admin"
}
```

- `groups: ["admins"]` -> `verify` risponde 200 alle richieste admin inoltrate.
- `manualVhost: true` -> `regenerateForwardAuthVhosts` salta questo host
  (non sovrascrive il vhost manuale con auth whole-host).
- `path` -> documentale; supportato da `verify.js` come check extra se presente.

## 4. Sviluppo locale (senza proxy)

Due opzioni:
- **Bypass totale**: `ADMIN_AUTH_DISABLED=1` -> backend tratta tutti come admin.
  Non impostarlo MAI in produzione.
- **Cookie reale**: se hai un cookie di sessione `.ai4educ.org` valido nel
  browser, il backend lo verifica presso `AI4AUTH_VERIFY_URL` e riconosce
  l'identita' senza segreto/proxy.

## Sicurezza

- Il segreto `X-Forwarded-Auth-Secret` impedisce lo spoofing degli header
  `Remote-*`: senza segreto valido il backend NON si fida e ricade sulla verifica
  cookie. Tenere `8002` comunque non esposto direttamente.
- `auth_request` non copre l'upgrade WebSocket: il backend risolve l'identita'
  (segreto o cookie) anche sull'handshake `/ws/stats`.
