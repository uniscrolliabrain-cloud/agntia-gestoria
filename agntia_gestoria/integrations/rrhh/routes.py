"""Superficie RRHH del middleware.

Todas las rutas resuelven la empresa desde el actor autenticado y exigen la
bandera de la etapa 1.1. Nada de esto escribe en Odoo ni ejecuta efectos.
"""
import json
import os
from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from ...auth import Actor, authenticate, company_access
from ...storage import identifier
from ..errors import IntegrationError, reject
from . import packs
from .config import config_for

CAPABILITIES = (
    'rrhh.policy.read',
    'rrhh.capabilities.read',
    'rrhh.health.read',
    'rrhh.closure.prepare',
    'rrhh.closure.read',
    'rrhh.closure.approve',
    'rrhh.closure.export',
    'rrhh.audit.read',
)


def pack_dir():
    value = os.getenv('GESTORIA_RRHH_PACKS')
    if not value:
        return None
    path = Path(value)
    return path if path.is_dir() else None


def load_sector(sector_id):
    directory = pack_dir()
    if directory is None:
        reject('configuration', 'No hay directorio de paquetes de sector configurado', 503)
    target = directory / f'{sector_id}.json'
    if not target.is_file():
        reject('not_found', 'Sector no encontrado', 404)
    return packs.load(packs.parse(target.read_text(encoding='utf-8'), source=target.name),
                      source=target.name)


async def integration_error(request, exc: IntegrationError):
    return JSONResponse({'detail': exc.public()}, status_code=exc.status)


def register_rrhh_routes(app, db):
    app.add_exception_handler(IntegrationError, integration_error)
    router = APIRouter(prefix='/api')

    def company(cid, actor):
        identifier(cid)
        company_access(actor, cid)
        return config_for(cid)

    @router.get('/companies/{cid}/rrhh/capabilities')
    def capabilities(cid, actor: Actor = Depends(authenticate)):
        config = company(cid, actor)
        return {'enabled': True, 'company_id': config.company_id, 'timezone': config.timezone,
                'policy_version': config.policy_version, 'payroll_provider': config.payroll_provider,
                'capabilities': list(CAPABILITIES)}

    @router.get('/companies/{cid}/rrhh/health')
    def health(cid, actor: Actor = Depends(authenticate)):
        config = company(cid, actor)
        with db.connection() as connection:
            snapshot = connection.execute(
                'SELECT body FROM objects WHERE company_id=? AND kind=? ORDER BY rowid DESC LIMIT 1',
                (identifier(cid), 'rrhh_snapshot')).fetchone()
        latest = json.loads(snapshot['body']) if snapshot else None
        return {'module': 'rrhh', 'enabled': True, 'timezone': config.timezone,
                'policy_version': config.policy_version,
                'provider': {'state': 'not_configured' if not config.payroll_provider else 'configured'},
                'snapshot': {'present': latest is not None,
                             'cutoff_at': latest.get('cutoff_at') if latest else None}}

    @router.get('/companies/{cid}/rrhh/policy')
    def policy(cid, actor: Actor = Depends(authenticate)):
        company(cid, actor)
        sector = os.getenv('GESTORIA_RRHH_SECTOR', '')
        if not sector:
            reject('configuration', 'Falta el sector de la empresa', 503)
        compiled = packs.compile_policy(load_sector(sector))
        return {'sector_id': compiled.sector_id, 'version': compiled.version,
                'sha256': compiled.sha256, 'legal_floor_version': compiled.legal_floor_version,
                'params': compiled.params,
                'rules': [{'id': rule['id'], 'base_legal': rule['base_legal']} for rule in compiled.rules]}

    app.include_router(router)
    return router
