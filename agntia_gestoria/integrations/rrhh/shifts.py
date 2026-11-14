"""Turnos: plantilla, cobertura, restricciones duras y publicación.

Antes de publicar se comprueban las restricciones que no se negocian: nadie en
dos turnos a la vez y descanso mínimo entre jornadas. Un cuadrante imposible se
rechaza con el motivo, no se publica «a medias».
"""
from datetime import datetime

from ...storage import Database, now, uid
from ..errors import reject

KIND = 'rrhh_shift_plan'
DEFAULT_REST_HOURS = 12


def _parse(value):
    return datetime.fromisoformat(value)


def validate(plan, *, rest_hours=DEFAULT_REST_HOURS):
    """Devuelve problemas; no publica nada si hay alguno."""
    problems = []
    by_employee = {}
    for slot in plan:
        by_employee.setdefault(slot['employee_ref'], []).append(slot)
    for employee, slots in sorted(by_employee.items()):
        ordered = sorted(slots, key=lambda item: item['starts_at'])
        for previous, current in zip(ordered, ordered[1:]):
            if _parse(current['starts_at']) < _parse(previous['ends_at']):
                problems.append({'employee_ref': employee, 'code': 'overlap',
                                 'at': current['starts_at'],
                                 'detail': 'Dos turnos solapados'})
                continue
            rest = (_parse(current['starts_at']) - _parse(previous['ends_at'])).total_seconds() / 3600
            if rest < rest_hours:
                problems.append({'employee_ref': employee, 'code': 'rest_below_minimum',
                                 'at': current['starts_at'],
                                 'detail': f'Descanso de {rest:.1f} h, mínimo {rest_hours} h'})
    return problems


def coverage(plan, required):
    """Quién cubre cada día y qué falta respecto a lo exigido (`{día: personas}`)."""
    counts = {}
    for slot in plan:
        day = slot['starts_at'][:10]
        counts[day] = counts.get(day, 0) + 1
    return {day: {'assigned': counts.get(day, 0), 'required': need,
                  'missing': max(0, need - counts.get(day, 0))}
            for day, need in sorted(required.items())}


def publish(connection, company_id, *, period, plan, required, actor, note=''):
    problems = validate(plan)
    if problems:
        reject('impossible_roster', f'Cuadrante imposible: {problems[0]["detail"]}', 409)
    gaps = [day for day, item in coverage(plan, required).items() if item['missing']]
    if gaps:
        reject('coverage_gap', f'Faltan personas el {gaps[0]}', 409)
    if not note or len(note.strip()) < 5:
        reject('reason_required', 'Publicar un cuadrante necesita una nota', 422)
    record = {'id': uid(), 'company_id': company_id, 'period': period, 'plan': list(plan),
              'coverage': coverage(plan, required), 'published_by': actor.id,
              'published_at': now(), 'note': note.strip(), 'state': 'published'}
    Database.put(connection, company_id, KIND, record,
                 unique_key=f'shift:{period}:{record["id"]}')
    return record


def republish(connection, company_id, previous, *, plan, actor, note):
    """Cambiar un cuadrante ya publicado crea una versión nueva y conserva la anterior."""
    record = publish(connection, company_id, period=previous['period'], plan=plan,
                     required={day: item['required'] for day, item in previous['coverage'].items()},
                     actor=actor, note=note)
    record['replaces'] = previous['id']
    Database.put(connection, company_id, KIND, record,
                 unique_key=f'shift:{record["period"]}:{record["id"]}')
    return record
