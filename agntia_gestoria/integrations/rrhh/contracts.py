"""Contratos versionados del middleware de RR. HH.

Esquemas mínimos y explícitos: duración en minutos enteros, fechas ISO con zona
y referencias opacas. Rechazan campos desconocidos para que un cambio de origen
no se cuele sin pasar por aquí.
"""
from ..errors import reject

SCHEMA_VERSION = 'rrhh-v1'
KINDS = ('employee', 'punch', 'absence', 'schedule', 'issue', 'closure',
         'approval', 'export', 'payroll_ack', 'document', 'case')

REQUIRED = {
    'employee': ('ref', 'display_name', 'active'),
    'punch': ('ref', 'employee_ref', 'at', 'direction'),
    'absence': ('ref', 'employee_ref', 'starts_at', 'ends_at', 'kind', 'state'),
    'schedule': ('employee_ref', 'weekday', 'minutes'),
    'issue': ('code', 'employee_ref', 'at', 'detail', 'base_legal'),
    'closure': ('period', 'policy_hash', 'snapshot_hash', 'employees', 'issues'),
    'approval': ('period', 'result_hash', 'approved_by', 'justification'),
    'export': ('period', 'manifest', 'exported_by'),
    'payroll_ack': ('period', 'provider', 'ref', 'totals'),
    'document': ('ref', 'employee_ref', 'kind', 'state'),
    'case': ('ref', 'employee_ref', 'kind', 'state', 'tasks'),
}

DIRECTIONS = ('in', 'out')
ABSENCE_STATES = ('pending', 'approved', 'rejected', 'revoked')


def _unknown(body, allowed):
    extra = sorted(set(body) - set(allowed))
    if extra:
        reject('unknown_field', f'Campos no admitidos: {", ".join(extra)}', 422)


def _requires(body, kind):
    missing = [key for key in REQUIRED[kind] if key not in body]
    if missing:
        reject('invalid_request', f'Faltan campos de {kind}: {", ".join(missing)}', 422)


def validate(kind, body, *, allow_extra=('id',)):
    if kind not in REQUIRED:
        reject('invalid_request', f'Tipo de contrato desconocido: {kind}', 422)
    if not isinstance(body, dict):
        reject('invalid_request', 'El cuerpo debe ser un objeto', 422)
    _requires(body, kind)
    _unknown(body, set(REQUIRED[kind]) | set(allow_extra))
    if kind == 'punch' and body['direction'] not in DIRECTIONS:
        reject('invalid_request', 'direction debe ser in u out', 422)
    if kind == 'absence' and body['state'] not in ABSENCE_STATES:
        reject('invalid_request', 'Estado de ausencia no admitido', 422)
    if kind == 'schedule' and not isinstance(body['minutes'], int):
        reject('invalid_request', 'minutes debe ser entero', 422)
    return {'schema': SCHEMA_VERSION, **body}


def period_parts(period):
    """`2026-10` → (2026, 10); valida formato y rango."""
    if not isinstance(period, str) or len(period) != 7 or period[4] != '-':
        reject('invalid_request', 'El periodo debe tener formato AAAA-MM', 422)
    year, month = period[:4], period[5:]
    if not (year.isdigit() and month.isdigit()) or not 1 <= int(month) <= 12:
        reject('invalid_request', 'El periodo debe tener formato AAAA-MM', 422)
    return int(year), int(month)


def minutes_from_hours(hours):
    """Horas decimales del origen → minutos enteros, sin redondeos ocultos."""
    try:
        value = float(hours)
    except (TypeError, ValueError):
        reject('invalid_request', 'Horas no numéricas', 422)
    if value < 0:
        reject('invalid_request', 'Horas negativas', 422)
    return int(round(value * 60))
