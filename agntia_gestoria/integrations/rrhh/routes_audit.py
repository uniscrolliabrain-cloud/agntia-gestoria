"""Lectura del rastro de auditoría del cierre."""
from fastapi import APIRouter, Depends

from ...auth import Actor, authenticate, company_access, require_role
from ...storage import identifier
from .audit import trail
from .config import config_for


def register_audit_routes(app, db):
    router = APIRouter(prefix='/api')

    @router.get('/companies/{cid}/rrhh/audit')
    def audit(cid, actor: Actor = Depends(authenticate)):
        identifier(cid)
        company_access(actor, cid)
        config_for(cid)
        require_role(actor, 'owner', 'reviewer')
        with db.connection() as connection:
            return trail(connection, cid)

    app.include_router(router)
    return router
