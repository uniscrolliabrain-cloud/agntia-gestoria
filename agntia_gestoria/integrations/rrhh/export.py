"""Exportación idempotente del cierre aprobado.

El manifiesto es lo que ve quien cobra: totales, horas por persona e incidencias,
sin datos personales. Repetir la exportación del mismo cierre devuelve el mismo
registro (`created=False`) en vez de duplicar efectos.
"""
import json

from ...storage import Database, digest, now, uid
from ..errors import reject
from .approval import verify_approval

EXPORT_ROLES = ('owner', 'reviewer')
KIND = 'rrhh_export'


def manifest(result, approval):
    counts = {}
    for issue in result.get('issues', []):
        counts[issue['code']] = counts.get(issue['code'], 0) + 1
    payload = {
        'period': result['period'],
        'policy_hash': result['policy_hash'],
        'snapshot_hash': result['snapshot_hash'],
        'result_hash': result['content_hash'],
        'approval_id': approval['id'],
        'approval_hash': approval['content_hash'],
        'totals': result['totals'],
        'issues': counts,
        'employees': {ref: {'minutes': item['minutes'], 'hours': item['hours']}
                      for ref, item in sorted(result['employees'].items())},
    }
    payload['content_hash'] = digest(payload)
    return payload


def export_period(connection, company_id, result, approval, actor):
    """Guarda el manifiesto una sola vez por cierre y lo devuelve."""
    verify_approval(approval, result)
    if actor.role not in EXPORT_ROLES:
        reject('forbidden', 'Tu rol no puede exportar un cierre', 403)
    Database.company(connection, company_id)
    payload = manifest(result, approval)
    key = f"export:{result['period']}:{payload['content_hash']}"
    existing = connection.execute(
        'SELECT body FROM objects WHERE company_id=? AND kind=? AND unique_key=?',
        (company_id, KIND, key)).fetchone()
    if existing:
        return json.loads(existing['body']), False
    body = {'id': uid(), 'company_id': company_id, 'exported_at': now(),
            'exported_by': actor.id, 'manifest': payload}
    Database.put(connection, company_id, KIND, body, unique_key=key)
    return body, True


def verify_export(body):
    payload = body['manifest']
    if digest({key: value for key, value in payload.items() if key != 'content_hash'}) != payload.get('content_hash'):
        reject('integrity', 'El manifiesto no coincide con su hash', 409)
    return body
