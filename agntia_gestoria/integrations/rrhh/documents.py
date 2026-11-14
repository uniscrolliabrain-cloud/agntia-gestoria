"""Documentos del expediente: caducidad, acuse de lectura y firma.

Un documento caducado no se sirve como vigente. Si se reemplaza después de pedir
la firma, no se finge que la firma vale para el nuevo: se abre un conflicto.
"""
from datetime import date

from ...storage import Database, now, uid
from ..errors import reject

KIND = 'rrhh_document'


def register(connection, company_id, *, employee_ref, kind, version, expires_at=None,
             requires_signature=False, actor=None):
    record = {'id': uid(), 'company_id': company_id, 'ref': uid(), 'employee_ref': employee_ref,
              'kind': kind, 'version': version, 'state': 'active', 'expires_at': expires_at,
              'requires_signature': requires_signature, 'signature': None,
              'read_by': [], 'registered_by': actor.id if actor else None,
              'registered_at': now(), 'history': []}
    Database.put(connection, company_id, KIND, record, unique_key=f"doc:{record['ref']}")
    return record


def expired(record, *, today=None):
    if not record.get('expires_at'):
        return False
    return date.fromisoformat(record['expires_at']) < (today or date.today())


def serve(record, *, today=None):
    if expired(record, today=today):
        reject('document_expired', 'El documento está caducado', 409)
    if record['state'] != 'active':
        reject('document_unavailable', 'El documento no está disponible', 409)
    return record


def mark_read(connection, company_id, record, *, reader_id):
    if reader_id not in record['read_by']:
        record['read_by'].append(reader_id)
        Database.put(connection, company_id, KIND, record, unique_key=f"doc:{record['ref']}")
    return record


def request_signature(connection, company_id, record, *, actor):
    if not record.get('requires_signature'):
        reject('invalid_request', 'El documento no requiere firma', 422)
    record['state'] = 'signature_pending'
    record['history'].append({'at': now(), 'by': actor.id, 'action': 'signature_requested'})
    Database.put(connection, company_id, KIND, record, unique_key=f"doc:{record['ref']}")
    return record


def replace_version(connection, company_id, record, *, version, actor):
    """Sustituir tras pedir firma no invalida en silencio: abre conflicto."""
    if record['state'] == 'signature_pending':
        record['state'] = 'signature_conflict'
        record['history'].append({'at': now(), 'by': actor.id, 'action': 'replaced_after_request',
                                  'note': 'Se pidió firma de la versión anterior'})
        Database.put(connection, company_id, KIND, record, unique_key=f"doc:{record['ref']}")
        reject('signature_conflict', 'El documento cambió después de pedir la firma', 409)
    record['version'] = version
    record['history'].append({'at': now(), 'by': actor.id, 'action': 'version_replaced'})
    Database.put(connection, company_id, KIND, record, unique_key=f"doc:{record['ref']}")
    return record
