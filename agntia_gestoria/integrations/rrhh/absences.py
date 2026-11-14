"""Ausencias y vacaciones: saldo, solapamiento, aprobación y revocación.

El saldo se calcula sobre la política versionada, no sobre una constante. El
solapamiento se bloquea antes de crear nada. La revocación no borra: añade un
paso al historial y deja la solicitud en `revoked`.
"""
from datetime import datetime

from ...storage import Database, now, uid
from ..errors import reject
from . import normalize

KIND = 'rrhh_absence'


def balance(policy, taken_days):
    allowed = int(policy.get('vacaciones_dias_naturales', 30))
    taken = max(0, int(taken_days))
    return {'allowed': allowed, 'taken': taken, 'remaining': max(0, allowed - taken)}


def _interval(item):
    return (datetime.fromisoformat(item['starts_at']), datetime.fromisoformat(item['ends_at']))


def check_overlap(existing, candidate):
    window = _interval(candidate)
    if window[1] <= window[0]:
        reject('invalid_request', 'La ausencia termina antes de empezar', 422)
    for item in existing:
        if item.get('state') == 'revoked':
            continue
        if normalize.overlaps(window, _interval(item)):
            reject('overlapping_absence', 'La ausencia se solapa con otra vigente', 409)
    return True


def create(connection, company_id, data, actor, *, existing=(), policy=None):
    check_overlap(existing, data)
    if policy is not None and data.get('kind') == 'vacaciones':
        taken = sum(1 for item in existing if item.get('kind') == 'vacaciones'
                    and item.get('state') in ('approved', 'pending'))
        if balance(policy, taken)['remaining'] <= 0:
            reject('no_balance', 'No quedan días de vacaciones en el saldo', 409)
    record = {'id': uid(), 'company_id': company_id, 'ref': data.get('ref') or uid(),
              'employee_ref': data['employee_ref'], 'starts_at': data['starts_at'],
              'ends_at': data['ends_at'], 'kind': data['kind'], 'state': 'pending',
              'reason': data.get('reason', ''), 'requested_by': actor.id,
              'history': [{'at': now(), 'by': actor.id, 'action': 'requested'}]}
    Database.put(connection, company_id, KIND, record, unique_key=f"absence:{record['ref']}")
    return record


def decide(connection, company_id, record, actor, *, approve, note=''):
    if record['state'] != 'pending':
        reject('invalid_state', 'Solo se decide sobre una ausencia pendiente', 409)
    if actor.id == record['requested_by']:
        reject('separation_of_duties', 'Quien solicita no puede decidir su ausencia', 403)
    record['state'] = 'approved' if approve else 'rejected'
    record['history'].append({'at': now(), 'by': actor.id,
                              'action': 'approved' if approve else 'rejected',
                              'note': note})
    Database.put(connection, company_id, KIND, record, unique_key=f"absence:{record['ref']}")
    return record


def revoke(connection, company_id, record, actor, *, reason):
    if record['state'] == 'revoked':
        return record
    if not reason or len(reason.strip()) < 5:
        reject('reason_required', 'La revocación necesita un motivo', 422)
    record['state'] = 'revoked'
    record['history'].append({'at': now(), 'by': actor.id, 'action': 'revoked',
                              'note': reason.strip()})
    Database.put(connection, company_id, KIND, record, unique_key=f"absence:{record['ref']}")
    return record


def visible(record, *, viewer_id, privileged):
    """El motivo solo lo ve quien solicita, quien decide o un rol privilegiado."""
    if privileged or viewer_id in (record['requested_by'],):
        return record
    return {**record, 'reason': ''}
