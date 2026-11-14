"""Incorporación y salida con expediente único.

La clave es estable por empleado y proceso, así que reintentar un alta no crea
un segundo expediente: devuelve el existente. Una baja no se completa mientras
queden tareas de revocación de accesos abiertas.
"""
import json

from ...storage import Database, now, uid
from ..errors import reject

KIND = 'rrhh_case'
ONBOARDING = ('contrato_firmado', 'datos_personales', 'equipo', 'accesos', 'formacion')
OFFBOARDING = ('devolucion_equipo', 'revocacion_accesos', 'liquidacion', 'entrevista_salida')


def _key(employee_ref, kind):
    return f'case:{employee_ref}:{kind}'


def open_case(connection, company_id, *, employee_ref, kind, actor, tasks=None):
    if kind not in ('onboarding', 'offboarding'):
        reject('invalid_request', 'El proceso debe ser onboarding u offboarding', 422)
    template = ONBOARDING if kind == 'onboarding' else OFFBOARDING
    key = _key(employee_ref, kind)
    row = connection.execute(
        'SELECT body FROM objects WHERE company_id=? AND kind=? AND unique_key=?',
        (company_id, KIND, key)).fetchone()
    if row:
        return json.loads(row['body']), False
    record = {'id': uid(), 'company_id': company_id, 'ref': uid(), 'employee_ref': employee_ref,
              'kind': kind, 'state': 'open', 'opened_by': actor.id, 'opened_at': now(),
              'tasks': [{'name': name, 'done': False, 'done_by': None, 'done_at': None}
                        for name in (tasks or template)]}
    Database.put(connection, company_id, KIND, record, unique_key=key)
    return record, True


def complete_task(connection, company_id, record, *, name, actor):
    names = [task['name'] for task in record['tasks']]
    if name not in names:
        reject('not_found', f'La tarea {name} no está en el expediente', 404)
    for task in record['tasks']:
        if task['name'] == name:
            if task['done']:
                return record
            task.update({'done': True, 'done_by': actor.id, 'done_at': now()})
    _close_if_ready(record)
    Database.put(connection, company_id, KIND, record,
                 unique_key=_key(record['employee_ref'], record['kind']))
    return record


def _close_if_ready(record):
    pending = [task['name'] for task in record['tasks'] if not task['done']]
    if not pending:
        record['state'] = 'closed'
        record['closed_at'] = now()
    else:
        record['state'] = 'open'
        record['pending'] = pending
    return record


def blockers(record):
    """Lo que impide cerrar una baja: normalmente, accesos sin revocar."""
    return [task['name'] for task in record['tasks'] if not task['done']]
