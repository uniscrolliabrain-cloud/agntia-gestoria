"""Superficie HTTP del cierre: preparar, aprobar y exportar.

El cierre se calcula sobre el snapshot ya guardado y la política compilada del
sector, así que las tres operaciones son reproducibles y auditables. Ninguna
escribe en Odoo: la exportación produce un manifiesto que otro paso entregará.
"""
import json
import os

from fastapi import APIRouter, Body, Depends

from ...auth import Actor, authenticate, company_access
from ...storage import Database, digest, identifier, now, uid
from ..errors import reject
from . import approval, engine, export, packs, snapshot
from .config import config_for
from .routes import load_sector

CLOSURE = 'rrhh_closure'
APPROVAL = 'rrhh_approval'
PREPARER_ROLES = ('owner', 'reviewer')
VOLATILE = ('id', 'created_at', 'content_hash')


def compiled_policy():
    sector = os.getenv('GESTORIA_RRHH_SECTOR', '')
    if not sector:
        reject('configuration', 'Falta el sector de la empresa', 503)
    return packs.compile_policy(load_sector(sector))


def policy_dict(policy):
    return {**policy.params, 'policy_hash': policy.sha256}


def one(connection, cid, kind, key):
    row = connection.execute(
        'SELECT body FROM objects WHERE company_id=? AND kind=? AND unique_key=?',
        (cid, kind, key)).fetchone()
    return json.loads(row['body']) if row else None


def latest(connection, cid, kind, prefix):
    row = connection.execute(
        'SELECT body FROM objects WHERE company_id=? AND kind=? AND unique_key LIKE ? '
        'ORDER BY rowid DESC LIMIT 1', (cid, kind, prefix)).fetchone()
    if not row:
        reject('not_found', 'No hay nada para ese periodo', 404)
    return json.loads(row['body'])


def closure_key(period, result_hash):
    return f'closure:{period}:{result_hash}'


def close(connection, cid, period, actor):
    policy = compiled_policy()
    source = snapshot.verify_snapshot(snapshot.load_snapshot(connection, cid, period))
    # El snapshot guarda las fuentes tal cual llegaron; el motor recibe los datos planos.
    data = {**source, **source.get('sources', {})}
    result = engine.close_period(data, policy_dict(policy))
    body = {'id': uid(), 'company_id': cid, 'period': period, 'prepared_by': actor.id,
            'created_at': now(), 'sector': {'id': policy.sector_id, 'version': policy.version,
                                            'sha256': policy.sha256}, 'result': result}
    body['content_hash'] = digest({key: value for key, value in body.items() if key not in VOLATILE})
    key = closure_key(period, result['content_hash'])
    existing = one(connection, cid, CLOSURE, key)
    if existing:
        return existing, False
    Database.put(connection, cid, CLOSURE, body, unique_key=key)
    return body, True


def register_closure_routes(app, db):
    router = APIRouter(prefix='/api')

    def company(cid, actor):
        identifier(cid)
        company_access(actor, cid)
        return config_for(cid)

    @router.post('/companies/{cid}/rrhh/closures')
    def prepare(cid, payload: dict = Body(...), actor: Actor = Depends(authenticate)):
        company(cid, actor)
        if actor.role not in PREPARER_ROLES:
            reject('forbidden', 'Tu rol no puede preparar un cierre', 403)
        period = payload.get('period')
        if not isinstance(period, str) or not period.strip():
            reject('invalid_request', 'Falta el periodo del cierre', 422)
        with db.transaction() as connection:
            body, created = close(connection, cid, period.strip(), actor)
        return {'closure': body, 'created': created}

    @router.get('/companies/{cid}/rrhh/closures/{period}')
    def read(cid, period, actor: Actor = Depends(authenticate)):
        company(cid, actor)
        with db.connection() as connection:
            return {'closure': latest(connection, cid, CLOSURE, f'closure:{period}:%')}

    @router.post('/companies/{cid}/rrhh/closures/{period}/approve')
    def sign(cid, period, payload: dict = Body(...), actor: Actor = Depends(authenticate)):
        company(cid, actor)
        with db.transaction() as connection:
            body = latest(connection, cid, CLOSURE, f'closure:{period}:%')
            record = approval.approve(
                body['result'], actor, prepared_by=body['prepared_by'],
                justification=payload.get('justification', ''),
                accepted_issues=payload.get('accepted_issues') or ())
            key = f"approval:{period}:{body['result']['content_hash']}:{record['approved_by']}"
            existing = one(connection, cid, APPROVAL, key)
            if existing:
                return {'approval': existing, 'created': False}
            Database.put(connection, cid, APPROVAL, record, unique_key=key)
        return {'approval': record, 'created': True}

    @router.post('/companies/{cid}/rrhh/closures/{period}/export')
    def deliver(cid, period, actor: Actor = Depends(authenticate)):
        company(cid, actor)
        with db.transaction() as connection:
            body = latest(connection, cid, CLOSURE, f'closure:{period}:%')
            result_hash = body['result']['content_hash']
            row = connection.execute(
                'SELECT body FROM objects WHERE company_id=? AND kind=? AND unique_key LIKE ? '
                'ORDER BY rowid DESC LIMIT 1',
                (cid, APPROVAL, f'approval:{period}:{result_hash}:%')).fetchone()
            if not row:
                reject('approval_required', 'El cierre necesita aprobación antes de exportarse', 409)
            document, created = export.export_period(
                connection, cid, body['result'], json.loads(row['body']), actor)
        return {'export': document, 'created': created}

    app.include_router(router)
    return router
