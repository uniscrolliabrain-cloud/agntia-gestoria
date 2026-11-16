"""Delegación de identidad verificada en servidor (campaña C03).

El runtime de Agente firma una aserción compacta y aquí se comprueban firma,
emisor, audiencia, vigencia, rol y alcance antes de ejecutar cualquier
capacidad. La aserción nunca puede conceder el rol ``owner``: representa a un
agente delegado, no a una persona propietaria. La clave vive solo en el
servidor y ninguna decisión se toma a partir de campos que envíe el cliente.
"""

import base64
import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass

from fastapi import HTTPException

from ..auth import Actor, authenticate
from .errors import reject

SCHEMA_VERSION = 1
DELEGATED_ROLES = ("agent", "viewer", "reviewer")
FORBIDDEN_ROLES = ("owner",)
SKEW_SECONDS = 60
MAX_ASSERTION_BYTES = 4096


@dataclass(frozen=True)
class Principal:
    """Actor delegado con su tenant y capacidades ya verificados."""

    id: str
    role: str
    companies: tuple[str, ...]
    tenant: str
    capabilities: tuple[str, ...]
    delegator: str
    expires_at: int

    def can_access(self, cid):
        return cid in self.companies


def _encode(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _decode(text):
    padding = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + padding)


def sign(claims, key):
    """Firma una aserción. Solo se usa en pruebas y en el emisor, nunca en el receptor."""
    payload = _encode(json.dumps(claims, sort_keys=True, separators=(",", ":")).encode())
    signature = hmac.new(key.encode(), payload.encode(), hashlib.sha256).digest()
    return payload + "." + _encode(signature)


def _capabilities():
    from . import policy

    return frozenset(policy.ALL)


def _key(configured=None):
    value = configured if configured is not None else os.getenv("GESTORIA_DELEGATION_KEY", "")
    if len(value) < 32:
        reject("not_configured", "La delegación de identidad no está configurada", 424)
    return value


def _audience(configured=None):
    return configured or os.getenv("GESTORIA_DELEGATION_AUDIENCE", "gestoria")


def _issuer():
    return os.getenv("GESTORIA_DELEGATION_ISSUER", "agente")


def verify(assertion, key=None, audience=None, now=None, issuer=None):
    """Devuelve un Principal o rechaza con un código tipado, nunca con detalle interno."""
    secret = _key(key)
    if not isinstance(assertion, str) or len(assertion) > MAX_ASSERTION_BYTES:
        reject("unsafe_principal", "Aserción de delegación inválida", 401)
    parts = assertion.split(".")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        reject("unsafe_principal", "Aserción de delegación inválida", 401)
    payload, signature = parts
    expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).digest()
    try:
        provided = _decode(signature)
    except Exception:
        provided = b""
    if not hmac.compare_digest(expected, provided):
        reject("unsafe_principal", "Aserción de delegación inválida", 401)
    try:
        claims = json.loads(_decode(payload))
    except Exception:
        reject("unsafe_principal", "Aserción de delegación inválida", 401)
    if not isinstance(claims, dict):
        reject("unsafe_principal", "Aserción de delegación inválida", 401)
    if claims.get("schema") != SCHEMA_VERSION:
        reject("unsafe_principal", "Versión de aserción no soportada", 401)
    if claims.get("aud") != _audience(audience):
        reject("unsafe_principal", "Audiencia de aserción incorrecta", 401)
    if claims.get("iss") != (issuer or _issuer()):
        reject("unsafe_principal", "Emisor de aserción no autorizado", 401)
    now = int(now if now is not None else time.time())
    expiry = claims.get("exp")
    issued = claims.get("iat")
    if type(expiry) is not int or type(issued) is not int:
        reject("unsafe_principal", "Aserción sin vigencia válida", 401)
    if expiry <= now:
        reject("principal_revoked", "La delegación ha caducado", 401)
    if issued > now + SKEW_SECONDS or expiry > now + 24 * 3600:
        reject("unsafe_principal", "Vigencia de aserción fuera de límite", 401)
    role = claims.get("role")
    if role in FORBIDDEN_ROLES or role not in DELEGATED_ROLES:
        reject("unsafe_principal", "La delegación no puede ostentar ese rol", 401)
    actor_id = claims.get("sub")
    if not isinstance(actor_id, str) or not 1 <= len(actor_id) <= 100:
        reject("unsafe_principal", "Identidad delegada inválida", 401)
    tenant = claims.get("tenant")
    if not isinstance(tenant, str) or not 1 <= len(tenant) <= 100:
        reject("unsafe_principal", "Tenant delegado inválido", 401)
    companies = claims.get("companies")
    if not isinstance(companies, list) or not companies or len(companies) > 100:
        reject("unsafe_principal", "Alcance de empresas inválido", 401)
    if any(not isinstance(item, str) or not 1 <= len(item) <= 64 for item in companies):
        reject("unsafe_principal", "Alcance de empresas inválido", 401)
    capabilities = claims.get("capabilities")
    allowed = _capabilities()
    if not isinstance(capabilities, list) or not capabilities:
        reject("unsafe_principal", "Alcance de capacidades inválido", 401)
    if any(not isinstance(item, str) or item not in allowed for item in capabilities):
        reject("forbidden", "La aserción solicita una capacidad desconocida", 403)
    delegator = claims.get("delegator")
    if not isinstance(delegator, str) or not 1 <= len(delegator) <= 100:
        reject("unsafe_principal", "Delegante inválido", 401)
    return Principal(
        id=actor_id,
        role=role,
        companies=tuple(dict.fromkeys(companies)),
        tenant=tenant,
        capabilities=tuple(dict.fromkeys(capabilities)),
        delegator=delegator,
        expires_at=expiry,
    )


def principal_from_request(request):
    """Identidad efectiva de una petición: aserción delegada o token local."""
    assertion = request.headers.get("X-Agente-Delegation", "")
    if not assertion:
        return authenticate(request)
    audience = request.headers.get("X-Agente-Audience") or None
    try:
        return verify(assertion, audience=audience)
    except HTTPException:
        raise
    except Exception as exc:
        from .errors import IntegrationError

        if isinstance(exc, IntegrationError):
            raise
        reject("unsafe_principal", "Aserción de delegación inválida", 401)


def is_delegated(actor):
    return isinstance(actor, Principal)


__all__ = ["Principal", "sign", "verify", "principal_from_request", "is_delegated", "SCHEMA_VERSION"]
