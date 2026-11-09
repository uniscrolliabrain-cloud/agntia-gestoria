import hmac
import json
import os
from dataclasses import dataclass

from fastapi import HTTPException, Request


@dataclass(frozen=True)
class Actor:
    id: str
    role: str
    companies: tuple[str, ...]

    def can_access(self, cid):
        return "*" in self.companies or cid in self.companies


def actors():
    values = json.loads(os.getenv("GESTORIA_ACTORS_JSON", "{}"))
    if not isinstance(values, dict):
        raise ValueError("GESTORIA_ACTORS_JSON debe ser un objeto")
    owner = os.getenv("GESTORIA_OWNER_TOKEN", "")
    if owner:
        values[owner] = {"id": "owner", "role": "owner", "companies": ["*"]}
    result = []
    for token, record in values.items():
        if len(token) < 16 or record.get("role") not in ("owner", "reviewer", "agent", "viewer") or not isinstance(record.get("id"), str) or not isinstance(record.get("companies"), list):
            raise ValueError("Credencial de actor inválida: revisa token, id, rol y empresas")
        result.append((token, Actor(record["id"], record["role"], tuple(record["companies"]))))
    return result


def authenticate(request: Request):
    configured = actors()
    if not configured:
        if request.client and request.client.host in ("127.0.0.1", "::1", "testclient"):
            return Actor("local-owner", "owner", ("*",))
        raise HTTPException(403, "Configura credenciales antes del acceso remoto")
    token = request.headers.get("Authorization", "").removeprefix("Bearer ") or request.cookies.get("gestoria_session", "")
    for secret, actor in configured:
        if hmac.compare_digest(secret.encode(), token.encode()):
            return actor
    raise HTTPException(401, "Credencial de acceso necesaria")


def require_role(actor, *roles):
    if actor.role not in roles:
        raise HTTPException(403, "Tu rol no permite esta operación")


def company_access(actor, cid):
    if not actor.can_access(cid):
        raise HTTPException(404, "Empresa no encontrada")
