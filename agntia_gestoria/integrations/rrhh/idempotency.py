"""Idempotencia de las operaciones con efecto.

La misma clave con el mismo contenido devuelve el trabajo existente. La misma
clave con contenido distinto es un conflicto, no una repetición. Si el proceso
cae a mitad, el registro queda `in_progress` y la reconciliación lo ve antes de
repetir cualquier efecto externo.
"""
import json

from ...storage import Database, digest, now, uid
from ..errors import reject

KIND = 'rrhh_idempotency'


def _key(key):
    return f'idem:{key}'


def begin(connection, company_id, key, payload, actor):
    if not isinstance(key, str) or len(key) < 8:
        reject('invalid_request', 'La clave de idempotencia es demasiado corta', 422)
    payload_hash = digest(payload)
    row = connection.execute(
        'SELECT body FROM objects WHERE company_id=? AND kind=? AND unique_key=?',
        (company_id, KIND, _key(key))).fetchone()
    if row:
        record = json.loads(row['body'])
        if record['payload_hash'] != payload_hash:
            reject('idempotency_conflict',
                   'La clave ya se usó con otro contenido', 409)
        return record, False
    record = {'id': uid(), 'company_id': company_id, 'key': key,
              'payload_hash': payload_hash, 'state': 'in_progress',
              'actor_id': actor.id, 'created_at': now()}
    Database.put(connection, company_id, KIND, record, unique_key=_key(key))
    return record, True


def finish(connection, company_id, key, result, *, state='done'):
    row = connection.execute(
        'SELECT body FROM objects WHERE company_id=? AND kind=? AND unique_key=?',
        (company_id, KIND, _key(key))).fetchone()
    if not row:
        reject('not_found', 'No hay operación con esa clave', 404)
    record = json.loads(row['body'])
    if record['state'] == 'done':
        return record
    record.update({'state': state, 'result': result, 'finished_at': now()})
    Database.put(connection, company_id, KIND, record, unique_key=_key(key))
    return record


def reconcile(connection, company_id, key):
    """Qué se sabe de una clave: sin registro, en curso o terminada."""
    row = connection.execute(
        'SELECT body FROM objects WHERE company_id=? AND kind=? AND unique_key=?',
        (company_id, KIND, _key(key))).fetchone()
    if not row:
        return {'known': False, 'state': 'unknown'}
    record = json.loads(row['body'])
    return {'known': True, 'state': record['state'],
            'result': record.get('result'), 'created_at': record['created_at']}
