"""Autenticazione tramite ai4auth (forward-auth).

Pattern allineato a counselorbot-sbs:
- percorso preferito: il proxy fidato inietta gli header `Remote-*` firmati con
  un segreto condiviso (`X-Forwarded-Auth-Secret` == FORWARD_AUTH_SHARED_SECRET);
- fallback: se il segreto non c'e' (proxy non ancora configurato), il backend
  valida il Cookie della richiesta direttamente presso ai4auth `/api/verify`
  prima di leggere l'identita'. Cosi' il login funziona anche con solo il cookie
  di dominio `.ai4educ.org`.
"""
import os
import secrets
from typing import Mapping

import httpx
from fastapi import Depends, HTTPException, Request, status

# Gruppo ai4auth che abilita la dashboard admin
ADMIN_GROUP = os.environ.get("ADMIN_GROUP", "admins")
FORWARD_AUTH_SHARED_SECRET = os.environ.get("FORWARD_AUTH_SHARED_SECRET", "")
AI4AUTH_VERIFY_URL = os.environ.get(
    "AI4AUTH_VERIFY_URL", "https://auth.ai4educ.org/api/verify"
).strip()
# Sviluppo locale senza proxy ne' cookie: tratta tutti come admin.
ADMIN_AUTH_DISABLED = os.environ.get("ADMIN_AUTH_DISABLED", "0") == "1"


def _parse_groups(raw: str):
    return [g.strip() for g in (raw or "").split(",") if g.strip()]


def _anonymous_identity() -> dict:
    return {
        "email": "",
        "username": "",
        "name": "",
        "groups": [],
        "is_admin": False,
        "authenticated": False,
    }


def _dev_identity() -> dict:
    return {
        "email": "dev@local",
        "username": "dev",
        "name": "Dev",
        "groups": [ADMIN_GROUP],
        "is_admin": True,
        "authenticated": True,
    }


def _identity_from_headers(headers: Mapping) -> dict:
    email = headers.get("Remote-Email", "") or ""
    username = headers.get("Remote-User", "") or ""
    name = headers.get("Remote-Name", "") or ""
    groups = _parse_groups(headers.get("Remote-Groups", ""))
    return {
        "email": email,
        "username": username or email,
        "name": name,
        "groups": groups,
        "is_admin": ADMIN_GROUP in groups,
        "authenticated": bool(username or email),
    }


async def resolve_identity(headers: Mapping) -> dict:
    """Identita' certificata dal proxy (segreto) o verificata via cookie."""
    if ADMIN_AUTH_DISABLED:
        return _dev_identity()

    supplied_secret = headers.get("X-Forwarded-Auth-Secret", "")
    trusted = bool(FORWARD_AUTH_SHARED_SECRET) and secrets.compare_digest(
        supplied_secret, FORWARD_AUTH_SHARED_SECRET
    )
    if trusted:
        return _identity_from_headers(headers)

    cookie = headers.get("Cookie", "")
    if not cookie or not AI4AUTH_VERIFY_URL:
        return _anonymous_identity()

    try:
        async with httpx.AsyncClient(timeout=4.0, follow_redirects=False) as client:
            response = await client.get(AI4AUTH_VERIFY_URL, headers={"Cookie": cookie})
        if response.status_code == 200:
            return _identity_from_headers(response.headers)
    except httpx.HTTPError:
        pass

    return _anonymous_identity()


async def get_identity(request: Request) -> dict:
    return await resolve_identity(request.headers)


async def get_current_user(identity: dict = Depends(get_identity)) -> dict:
    if not identity["authenticated"]:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Non autenticato")
    return identity


async def get_current_active_admin(identity: dict = Depends(get_current_user)) -> dict:
    if not identity["is_admin"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Accesso riservato agli amministratori")
    return identity
