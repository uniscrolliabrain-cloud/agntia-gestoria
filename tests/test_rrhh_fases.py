import pytest

from agntia_gestoria.auth import Actor
from agntia_gestoria.integrations.errors import IntegrationError
from agntia_gestoria.integrations.rrhh import (contracts, idempotency, normalize, scope,
                                               source, workflow)
from agntia_gestoria.storage import Database, canonical

CID = 'a' * 32
OTHER = 'b' * 32
OWNER = Actor('marta', 'owner', ('*',))
REVIEWER = Actor('luis', 'reviewer', (CID,))
VIEWER = Actor('vero', 'viewer', (CID,))


def code_of(call):
    with pytest.raises(IntegrationError) as error:
        call()
    return error.value.code, error.value.status


def database(tmp_path):
    db = Database(str(tmp_path))
    with db.transaction() as connection:
        connection.execute('INSERT INTO companies(id,body) VALUES(?,?)',
                           (CID, canonical({'id': CID, 'name': 'Uno'})))
    return db


def test_contracts_reject_unknown_fields_and_normalise_minutes():
    punch = contracts.validate('punch', {'ref': 'p1', 'employee_ref': 'e1',
                                         'at': '2026-10-05T08:00:00+02:00', 'direction': 'in'})
    assert punch['schema'] == contracts.SCHEMA_VERSION
    assert code_of(lambda: contracts.validate('punch', {
        'ref': 'p1', 'employee_ref': 'e1', 'at': '2026-10-05T08:00:00+02:00',
        'direction': 'in', 'sueldo': 1}))[0] == 'unknown_field'
    assert code_of(lambda: contracts.validate('punch', {'ref': 'p1'}))[0] == 'invalid_request'
    assert contracts.minutes_from_hours('7.75') == 465
    assert contracts.period_parts('2026-10') == (2026, 10)
    assert code_of(lambda: contracts.period_parts('2026-13'))[0] == 'invalid_request'


def test_scope_resolves_from_the_actor_and_refuses_other_company():
    context = scope.resolve(REVIEWER, CID, capabilities=('rrhh.read',))
    assert context.company_id == CID and context.allows('rrhh.read')
    assert not context.allows('rrhh.closure.approve')
    assert scope.resolve(OWNER, CID).allows('cualquiera')
    assert code_of(lambda: scope.resolve(VIEWER, 'nohex'))[0] == 'invalid_request'
    assert code_of(lambda: scope.same_company(context, OTHER))[0] == 'scope_violation'
    assert code_of(lambda: scope.require(context, 'rrhh.closure.approve'))[0] == 'forbidden'


def test_normalisation_uses_absolute_time_and_splits_nights():
    start = normalize.to_local('2026-10-05T22:00:00+02:00', 'Europe/Madrid')
    end = normalize.to_local('2026-10-06T06:00:00+02:00', 'Europe/Madrid')
    assert normalize.minutes_between(start, end) == 480
    chunks = normalize.split_by_day(start, end, 'Europe/Madrid')
    assert len(chunks) == 2
    assert sum(normalize.minutes_between(a, b) for a, b in chunks) == 480
    assert code_of(lambda: normalize.zone('Marte/Olympus'))[0] == 'configuration'


def test_source_paginates_and_refuses_out_of_scope_records():
    employees = [{'ref': f'e{index}', 'display_name': f'E{index}', 'active': True}
                 for index in range(5)]
    memory = source.MemorySource(employees=employees, page_size=2)
    data = source.read_period(memory, CID, '2026-10')
    assert len(data['employees']) == 5
    assert data['marker'] == 'm1'

    leaky = source.MemorySource(employees=[{'ref': 'x', 'company_id': OTHER}])
    assert code_of(lambda: source.read_period(leaky, CID, '2026-10'))[0] == 'outside_scope'
    assert code_of(lambda: source.read_period(source.Unavailable(), CID, '2026-10')) == (
        'capability_unavailable', 503)


def test_source_rejects_a_cursor_loop():
    class Looping(source.Source):
        def marker(self, company_id):
            return 'm'

        def employees(self, company_id, cursor=None):
            return source.Page(({'ref': 'e1'},), 'same')

        def punches(self, company_id, period, cursor=None):
            return source.Page((), None)

        def absences(self, company_id, period, cursor=None):
            return source.Page((), None)

    assert code_of(lambda: source.read_period(Looping(), CID, '2026-10'))[0] == 'source_contract'


def test_idempotency_returns_the_same_work_and_refuses_another_payload(tmp_path):
    db = database(tmp_path)
    with db.transaction() as connection:
        first, created = idempotency.begin(connection, CID, 'clave-larga-1', {'period': '2026-10'}, OWNER)
        again, created_again = idempotency.begin(connection, CID, 'clave-larga-1', {'period': '2026-10'}, OWNER)
        state = idempotency.reconcile(connection, CID, 'clave-larga-1')['state']
    assert created is True and created_again is False
    assert first['id'] == again['id']
    assert state == 'in_progress'
    with db.transaction() as connection:
        code, status = code_of(lambda: idempotency.begin(
            connection, CID, 'clave-larga-1', {'period': '2026-11'}, OWNER))
    assert (code, status) == ('idempotency_conflict', 409)


def test_idempotency_finishes_and_reports_result(tmp_path):
    db = database(tmp_path)
    with db.transaction() as connection:
        idempotency.begin(connection, CID, 'clave-larga-2', {'x': 1}, OWNER)
        done = idempotency.finish(connection, CID, 'clave-larga-2', {'closure': 'ok'})
        again = idempotency.finish(connection, CID, 'clave-larga-2', {'closure': 'otro'})
        settled = idempotency.reconcile(connection, CID, 'clave-larga-2')
    assert done['state'] == 'done' and again['result'] == {'closure': 'ok'}
    assert settled['result'] == {'closure': 'ok'}


def test_workflow_needs_role_reason_and_evidence():
    step = workflow.apply('prepared', 'pending_review', REVIEWER, reason='Listo para revisión',
                          evidence={'closure': 'c1'})
    assert step['next'] == ['approved', 'prepared']
    assert code_of(lambda: workflow.apply('prepared', 'exported', OWNER, reason='atajo',
                                          evidence={'x': 1}))[0] == 'invalid_transition'
    assert code_of(lambda: workflow.apply('prepared', 'pending_review', VIEWER,
                                          reason='sin rol', evidence={'x': 1}))[0] == 'forbidden'
    assert code_of(lambda: workflow.apply('prepared', 'pending_review', REVIEWER,
                                          reason='', evidence={'x': 1}))[0] == 'reason_required'
    assert code_of(lambda: workflow.apply('prepared', 'pending_review', REVIEWER,
                                          reason='sin evidencia', evidence=None))[0] == 'evidence_required'
    assert workflow.describe('exported')['terminal'] is True
