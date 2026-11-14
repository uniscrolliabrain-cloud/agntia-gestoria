"""Rastro append-only del cierre y comprobación de su cadena.

Cada operación que cambia estado deja un evento enlazado con el anterior, así
que borrar o reescribir un evento se detecta al recorrer la cadena. El rastro no
guarda salarios ni datos personales, solo actor, acción, objeto y hashes.
"""
from ...storage import Database, digest

ZERO = '0' * 64


def record(connection, cid, actor, action, object_id, body):
    Database.audit(connection, cid, actor, action, object_id, body)


def trail(connection, cid):
    """Devuelve la cadena y dónde se rompe, si se rompe."""
    events = Database.audit_log(connection, cid)
    previous = ZERO
    broken = None
    for event in events:
        content = {key: value for key, value in event.items() if key not in ('hash', 'sequence')}
        if event['previous_hash'] != previous or digest(content) != event['hash']:
            broken = event['sequence']
            break
        previous = event['hash']
    return {'valid': broken is None, 'events': len(events), 'broken_at': broken,
            'last_hash': previous,
            'actions': [event['action'] for event in events]}
