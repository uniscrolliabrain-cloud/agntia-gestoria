"""Ámbito resuelto en servidor: tenant, empresa, actor y capacidad.

La empresa nunca se toma del cuerpo ni de una cabecera libre: se resuelve desde
el actor autenticado y la configuración del host. Un identificador de otra
empresa es `scope_violation` antes de leer o escribir nada.
"""
from dataclasses import dataclass

from ...auth import company_access
from ...storage import identifier
from ..errors import reject


@dataclass(frozen=True)
class Context:
    tenant_id: str
    company_id: str
    actor_id: str
    role: str
    capabilities: tuple

    def allows(self, capability):
        if self.role == 'owner':
            return True
        return capability in self.capabilities


def resolve(actor, company_id, *, capabilities=()):
    try:
        cid = identifier(company_id)
    except ValueError:
        reject('invalid_request', 'Identificador de empresa inválido', 422)
    company_access(actor, cid)
    return Context(tenant_id=cid, company_id=cid, actor_id=actor.id, role=actor.role,
                   capabilities=tuple(capabilities))


def require(context, capability):
    if not context.allows(capability):
        reject('forbidden', f'Falta la capacidad {capability}', 403)
    return context


def same_company(context, other_company):
    """Cualquier referencia con otra empresa se rechaza, no se ignora."""
    if not isinstance(other_company, str) or other_company != context.company_id:
        reject('scope_violation', 'La referencia pertenece a otra empresa', 403)
    return True
