"""Motor determinista del cierre. Sin IO, sin reloj, sin entorno.

Recibe un snapshot y una política ya compilada y devuelve horas por persona,
incidencias explicadas y un hash del resultado. La misma entrada da el mismo
byte de salida; cualquier cambio de política o de datos cambia el hash.
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from ...storage import digest

BREAK_MINUTES = 15
BREAK_THRESHOLD_MINUTES = 360
DAILY_MAX_MINUTES = 540


@dataclass(frozen=True)
class Issue:
    code: str
    employee_ref: str
    at: str
    detail: str
    base_legal: str

    def as_dict(self):
        return {'code': self.code, 'employee_ref': self.employee_ref, 'at': self.at,
                'detail': self.detail, 'base_legal': self.base_legal}


def _parse(value):
    return datetime.fromisoformat(value)


def pair_punches(punches, employee_ref):
    """Empareja entrada y salida en orden temporal; devuelve intervalos e incidencias."""
    ordered = sorted(punches, key=lambda item: item['at'])
    intervals, issues, open_punch = [], [], None
    for punch in ordered:
        if punch['direction'] == 'in':
            if open_punch is not None:
                issues.append(Issue('duplicate_punch', employee_ref, punch['at'],
                                    'Entrada sin salida previa', 'art. 34.9 ET'))
            open_punch = punch
            continue
        if open_punch is None:
            issues.append(Issue('incomplete_punch', employee_ref, punch['at'],
                                'Salida sin entrada previa', 'art. 34.9 ET'))
            continue
        start, end = _parse(open_punch['at']), _parse(punch['at'])
        if end <= start:
            issues.append(Issue('incomplete_punch', employee_ref, punch['at'],
                                'Intervalo no positivo', 'art. 34.9 ET'))
        else:
            intervals.append((start, end, open_punch, punch))
        open_punch = None
    if open_punch is not None:
        issues.append(Issue('incomplete_punch', employee_ref, open_punch['at'],
                            'Entrada sin salida', 'art. 34.9 ET'))
    return intervals, issues


def net_minutes(start, end):
    """Minutos trabajados de un intervalo, con la pausa del art. 34.4 si procede."""
    gross = int((end - start).total_seconds() // 60)
    if gross > BREAK_THRESHOLD_MINUTES:
        return gross - BREAK_MINUTES
    return gross


def close_period(snapshot, policy):
    """Cierre reproducible: horas por persona, incidencias y hash del resultado."""
    issues = []
    by_employee = {}
    holidays = set(policy.get('holidays', ()))
    daily_max = int(policy.get('jornada_diaria_horas_max', DAILY_MAX_MINUTES / 60)) * 60

    for employee in sorted(snapshot['employees'], key=lambda item: item['ref']):
        ref = employee['ref']
        intervals, employee_issues = pair_punches(employee.get('punches', []), ref)
        issues.extend(employee_issues)
        minutes = 0
        by_day = {}
        for start, end, _, _ in intervals:
            worked = net_minutes(start, end)
            minutes += worked
            day = start.date().isoformat()
            by_day[day] = by_day.get(day, 0) + worked
            if start.date() != end.date():
                issues.append(Issue('crosses_midnight', ref, start.isoformat(),
                                    'Intervalo que cruza medianoche', 'art. 34.3 ET'))
        for day, total in sorted(by_day.items()):
            if total > daily_max:
                issues.append(Issue('daily_hours_exceeded', ref, day,
                                    f'{total} minutos sobre {daily_max}', 'art. 34.3 ET'))
            if day in holidays and total:
                issues.append(Issue('worked_on_holiday', ref, day,
                                    'Trabajo en festivo sin compensación registrada', 'art. 37.2 ET'))
        for absence in employee.get('absences', []):
            if absence['state'] == 'pending':
                issues.append(Issue('pending_absence', ref, absence['starts_at'],
                                    'Ausencia sin aprobar', 'art. 38.3 ET'))
        if not intervals and not employee.get('absences'):
            issues.append(Issue('missing_punch', ref, snapshot['period'],
                                'Sin fichajes ni ausencias en el periodo', 'art. 34.9 ET'))
        by_employee[ref] = {'minutes': minutes, 'hours': str(Decimal(minutes) / Decimal(60)),
                            'intervals': len(intervals)}

    payload = {'period': snapshot['period'], 'policy_hash': policy['policy_hash'],
               'snapshot_hash': snapshot['content_hash'], 'employees': by_employee,
               'issues': [issue.as_dict() for issue in issues]}
    payload['content_hash'] = digest(payload)
    payload['totals'] = {'employees': len(by_employee),
                         'minutes': sum(item['minutes'] for item in by_employee.values()),
                         'issues': len(issues)}
    return payload


def replay(result):
    """Huella para comprobar que un recálculo devuelve exactamente lo mismo."""
    return digest({key: result[key] for key in ('period', 'policy_hash', 'snapshot_hash',
                                                'employees', 'issues')})


def transition(current, target, actor, reason, evidence):
    """Transiciones permitidas del cierre, con actor, motivo y evidencia."""
    allowed = {
        'prepared': {'blocked', 'pending_review'},
        'pending_review': {'approved', 'prepared'},
        'approved': {'exported', 'pending_review'},
        'blocked': {'prepared'},
        'exported': {'reconciliation_required'},
        'reconciliation_required': {'exported'},
    }
    if target not in allowed.get(current, set()):
        raise ValueError(f'Transición no permitida: {current} -> {target}')
    if not actor or not reason or not evidence:
        raise ValueError('Toda transición necesita actor, motivo y evidencia')
    return {'from': current, 'to': target, 'actor_id': actor, 'reason': reason,
            'evidence': evidence}
