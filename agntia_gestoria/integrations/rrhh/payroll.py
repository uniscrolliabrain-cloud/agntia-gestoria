"""Nómina: exportación de incidencias aprobadas y conciliación de acuses.

El middleware no calcula nómina. Exporta lo aprobado en un formato versionado
con totales y una clave estable por periodo y proveedor; el acuse se compara
contra esos totales. Si no cuadra, es conflicto, no un aviso para seguir.
"""
from ...storage import Database, digest, now, uid
from ..errors import reject

KIND = 'rrhh_payroll_ack'
FORMAT = 'payroll-incidents-v1'


def build(closure, approval, *, provider):
    """Solo lo aprobado; sin aprobación vigente no hay exportación."""
    if not provider:
        reject('capability_unavailable', 'No hay proveedor de nómina configurado', 503)
    if approval.get('result_hash') != closure['result']['content_hash']:
        reject('approval_stale', 'La aprobación no corresponde a este cierre', 409)
    incidents = []
    for ref, employee in sorted(closure['result']['employees'].items()):
        incidents.append({'employee_ref': ref, 'minutes': employee['minutes'],
                          'hours': employee['hours']})
    totals = {'employees': len(incidents),
              'minutes': sum(item['minutes'] for item in incidents)}
    document = {'format': FORMAT, 'period': closure['period'], 'provider': provider,
                'approval_id': approval['id'], 'incidents': incidents, 'totals': totals}
    document['content_hash'] = digest(document)
    return document


def record_ack(connection, company_id, document, *, ref, totals):
    expected = document['totals']
    if totals.get('minutes') != expected['minutes'] or totals.get('employees') != expected['employees']:
        reject('payroll_mismatch', 'El acuse no cuadra con los totales exportados', 409)
    record = {'id': uid(), 'company_id': company_id, 'period': document['period'],
              'provider': document['provider'], 'ref': ref, 'totals': totals,
              'document_hash': document['content_hash'], 'state': 'reconciled',
              'received_at': now()}
    Database.put(connection, company_id, KIND, record,
                 unique_key=f"ack:{document['period']}:{document['provider']}:{ref}")
    return record


def reexport(connection, company_id, document, *, reason):
    """Reenviar no duplica: misma clave de documento si los totales no cambiaron."""
    if document['content_hash'] != digest({key: value for key, value in document.items()
                                            if key != 'content_hash'}):
        reject('integrity', 'El documento exportado no cuadra con su hash', 409)
    if not reason or len(reason.strip()) < 5:
        reject('reason_required', 'Un reenvío necesita motivo', 422)
    return {'document': document, 'key': f"payroll:{document['period']}:{document['content_hash']}",
            'reason': reason.strip()}
