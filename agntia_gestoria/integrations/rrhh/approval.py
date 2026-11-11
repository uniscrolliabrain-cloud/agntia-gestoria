"""Aprobación del cierre ligada a hashes.

Aprobar no es un estado que se recuerda: es un registro que firma un resultado
concreto (snapshot, política, horas e incidencias). Si el cierre se recalcula y
cambia, la aprobación deja de valer y hay que revisarlo otra vez. Quien prepara
el cierre no puede aprobarlo, y cada tipo de incidencia se acepta por separado.
"""
from ...storage import digest, now, uid
from ..errors import reject

APPROVER_ROLES = ('owner', 'reviewer')
MIN_JUSTIFICATION = 10


def _codes(result):
    return sorted({issue['code'] for issue in result.get('issues', [])})


def approve(result, actor, *, prepared_by, justification, accepted_issues=()):
    """Devuelve el registro firmado o rechaza con el motivo concreto."""
    if actor.role not in APPROVER_ROLES:
        reject('forbidden', 'Tu rol no puede aprobar un cierre', 403)
    if not prepared_by:
        reject('unattributed', 'Falta quién preparó el cierre', 422)
    if prepared_by == actor.id:
        reject('separation_of_duties', 'Quien prepara el cierre no puede aprobarlo', 403)
    if not isinstance(justification, str) or len(justification.strip()) < MIN_JUSTIFICATION:
        reject('justification_required',
               f'La aprobación necesita un motivo de al menos {MIN_JUSTIFICATION} caracteres', 422)

    present = _codes(result)
    unknown = sorted(set(accepted_issues) - set(present))
    if unknown:
        reject('unknown_issue', f'Incidencias que no están en el cierre: {", ".join(unknown)}', 422)
    pending = sorted(set(present) - set(accepted_issues))
    if pending:
        reject('unreviewed_issues',
               f'Hay incidencias sin aceptar: {", ".join(pending)}', 409)

    counts = {}
    for issue in result.get('issues', []):
        counts[issue['code']] = counts.get(issue['code'], 0) + 1

    record = {
        'id': uid(),
        'period': result['period'],
        'policy_hash': result['policy_hash'],
        'snapshot_hash': result['snapshot_hash'],
        'result_hash': result['content_hash'],
        'prepared_by': prepared_by,
        'approved_by': actor.id,
        'approved_role': actor.role,
        'approved_at': now(),
        'justification': justification.strip(),
        'accepted_issues': sorted(accepted_issues),
        'acknowledged': counts,
    }
    record['content_hash'] = digest(record)
    return record


def verify_approval(record, result):
    """Una aprobación solo vale para el cierre exacto que firmó."""
    if digest({key: value for key, value in record.items() if key != 'content_hash'}) != record.get('content_hash'):
        reject('integrity', 'La aprobación no coincide con su hash', 409)
    if record.get('result_hash') != result.get('content_hash'):
        reject('approval_stale', 'El cierre cambió después de aprobarse', 409)
    if record.get('policy_hash') != result.get('policy_hash') or \
            record.get('snapshot_hash') != result.get('snapshot_hash'):
        reject('approval_stale', 'La política o el snapshot cambiaron después de aprobarse', 409)
    return record
