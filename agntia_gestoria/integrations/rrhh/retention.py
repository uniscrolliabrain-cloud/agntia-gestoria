"""Retención y copias: purga lo caducado, jamás lo vigente.

La ventana propuesta es de 42 días para material de trabajo; el registro horario
que exige conservación legal no se purga aquí. Una copia se conserva con su
fecha y su hash para poder demostrar qué se restauró.
"""
from datetime import date, timedelta

from ..errors import reject

DEFAULT_DAYS = 42


def cutoff(today=None, *, days=DEFAULT_DAYS):
    return (today or date.today()) - timedelta(days=days)


def purgeable(records, *, today=None, days=DEFAULT_DAYS, keep=()):
    """Separa lo purgable de lo que hay que conservar, explicando por qué."""
    limit = cutoff(today, days=days)
    keep = set(keep)
    expired, retained = [], []
    for record in records:
        if record.get('id') in keep or record.get('legal_hold'):
            retained.append({'id': record.get('id'), 'reason': 'vigente o retenido'})
            continue
        created = record.get('created_at')
        if not created:
            retained.append({'id': record.get('id'), 'reason': 'sin fecha de creación'})
            continue
        moment = date.fromisoformat(created[:10])
        if moment < limit:
            expired.append(record.get('id'))
        else:
            retained.append({'id': record.get('id'), 'reason': 'dentro de ventana'})
    return {'cutoff': limit.isoformat(), 'purge': expired, 'retain': retained}


def purge(records, *, today=None, days=DEFAULT_DAYS, keep=()):
    plan = purgeable(records, today=today, days=days, keep=keep)
    doomed = set(plan['purge'])
    return {'deleted': len(doomed), 'kept': len(records) - len(doomed), 'plan': plan}


def backup_record(*, at, path, sha256, size_bytes):
    if not path or not sha256:
        reject('invalid_request', 'La copia necesita ruta y hash', 422)
    return {'at': at, 'path': path, 'sha256': sha256, 'size_bytes': int(size_bytes)}


def rotation(backups, *, keep=7):
    """Conserva las N más recientes y marca el resto para borrar."""
    ordered = sorted(backups, key=lambda item: item['at'], reverse=True)
    return {'keep': ordered[:keep], 'delete': ordered[keep:]}


def legal_hold(record):
    """El registro horario obligatorio no entra en la purga de trabajo."""
    return {**record, 'legal_hold': True}
