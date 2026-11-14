"""Snapshot inmutable del periodo.

La frescura se comprueba **dentro** de la transacción: se lee el marcador del
origen, se construye el cuerpo y se vuelve a leer antes de escribir. Si cambió,
no se guarda nada y se responde `source_changed` (409).
"""
import json

from ...storage import Database, digest, now, uid
from ..errors import reject

# Campos volátiles: identificador y sello de corte cambian entre intentos y no
# forman parte de lo que se firma. El hash cubre periodo, política y fuentes.
VOLATILE = ('id', 'cutoff_at', 'content_hash')


def _hashed(body):
    return {key: value for key, value in body.items() if key not in VOLATILE}


def snapshot_body(company_id, period, sources, *, policy_hash, timezone, cutoff_at=None):
    payload = {'id': uid(), 'company_id': company_id, 'period': period, 'timezone': timezone,
               'policy_hash': policy_hash, 'cutoff_at': cutoff_at or now(),
               'sources': sources}
    payload['content_hash'] = digest(_hashed(payload))
    return payload


def persist_snapshot(connection, company_id, period, read, *, policy_hash, timezone):
    """`read()` devuelve `{'marker': str, 'sources': {...}}`; se llama dos veces."""
    Database.company(connection, company_id)
    first = read()
    body = snapshot_body(company_id, period, first['sources'],
                         policy_hash=policy_hash, timezone=timezone)
    second = read()
    if second['marker'] != first['marker']:
        reject('source_changed', 'El origen cambió mientras se preparaba el cierre', 409)
    key = f"snapshot:{period}:{body['content_hash']}"
    existing = connection.execute(
        'SELECT body FROM objects WHERE company_id=? AND kind=? AND unique_key=?',
        (company_id, 'rrhh_snapshot', key)).fetchone()
    if existing:
        return json.loads(existing['body']), False
    Database.put(connection, company_id, 'rrhh_snapshot', body, unique_key=key)
    return body, True


def load_snapshot(connection, company_id, period):
    row = connection.execute(
        'SELECT body FROM objects WHERE company_id=? AND kind=? AND unique_key LIKE ? '
        'ORDER BY rowid DESC LIMIT 1',
        (company_id, 'rrhh_snapshot', f'snapshot:{period}:%')).fetchone()
    if not row:
        reject('not_found', 'No hay snapshot para ese periodo', 404)
    return json.loads(row['body'])


def verify_snapshot(snapshot):
    """Un snapshot manipulado no se usa: se detecta por su propio hash."""
    if digest(_hashed(snapshot)) != snapshot.get('content_hash'):
        reject('integrity', 'El snapshot no coincide con su hash', 409)
    return snapshot
