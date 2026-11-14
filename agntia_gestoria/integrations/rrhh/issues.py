"""Catálogo de incidencias: código, gravedad, norma y siguiente paso.

Un cierre no dice «hay un problema»: dice qué pasa, qué norma lo sostiene y qué
puede hacer una persona. El catálogo es la única fuente de esa explicación.
"""
from ..errors import reject

CATALOGUE = {
    'incomplete_punch': ('high', 'art. 34.9 ET', 'Completar o corregir el fichaje'),
    'duplicate_punch': ('high', 'art. 34.9 ET', 'Revisar el fichaje duplicado'),
    'crosses_midnight': ('medium', 'art. 34.3 ET', 'Confirmar el turno de noche'),
    'daily_hours_exceeded': ('high', 'art. 34.3 ET', 'Revisar el exceso diario'),
    'worked_on_holiday': ('medium', 'art. 37.2 ET', 'Registrar la compensación'),
    'pending_absence': ('medium', 'art. 38.3 ET', 'Aprobar o rechazar la ausencia'),
    'missing_punch': ('medium', 'art. 34.9 ET', 'Registrar actividad del periodo'),
    'wrong_center': ('high', 'art. 34.9 ET', 'Corregir el centro del fichaje'),
    'outside_scope': ('critical', 'RGPD art. 5', 'Investigar el acceso fuera de ámbito'),
    'overlapping_absence': ('high', 'art. 38.3 ET', 'Resolver el solapamiento'),
    'document_expired': ('medium', 'art. 21 ET', 'Renovar el documento'),
    'signature_conflict': ('high', 'ley 6/2020', 'Revisar la firma solicitada'),
}

SEVERITY_ORDER = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}


def describe(code):
    if code not in CATALOGUE:
        reject('unknown_issue', f'Incidencia desconocida: {code}', 422)
    severity, base_legal, next_action = CATALOGUE[code]
    return {'code': code, 'severity': severity, 'base_legal': base_legal,
            'next_action': next_action}


def build(code, employee_ref, at, detail):
    return {'employee_ref': employee_ref, 'at': at, 'detail': detail, **describe(code)}


def summarize(issues):
    """Cuenta por código y ordena por gravedad para la portada del cierre."""
    groups = {}
    for issue in issues:
        item = groups.setdefault(issue['code'], {'count': 0, 'severity': issue['severity'],
                                                 'next_action': issue['next_action'],
                                                 'base_legal': issue['base_legal']})
        item['count'] += 1
    return sorted(({'code': code, **data} for code, data in groups.items()),
                  key=lambda item: (SEVERITY_ORDER.get(item['severity'], 9), item['code']))


def actionable(issues):
    """Las que bloquean exportación hasta que alguien decide."""
    return [issue for issue in issues if issue['severity'] in ('critical', 'high')]
