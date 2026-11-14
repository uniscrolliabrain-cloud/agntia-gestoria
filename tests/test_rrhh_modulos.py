import json

import pytest

from agntia_gestoria.auth import Actor
from agntia_gestoria.integrations.errors import IntegrationError
from agntia_gestoria.integrations.rrhh import (absences, documents, onboarding, payroll,
                                               shifts)
from agntia_gestoria.storage import Database, canonical

CID = 'a' * 32
OWNER = Actor('marta', 'owner', ('*',))
REVIEWER = Actor('luis', 'reviewer', (CID,))
POLICY = {'vacaciones_dias_naturales': 30}


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


def absence(**extra):
    return {'employee_ref': 'e1', 'starts_at': '2026-10-12T00:00:00+02:00',
            'ends_at': '2026-10-16T00:00:00+02:00', 'kind': 'vacaciones', **extra}


def test_absence_balance_overlap_and_decision(tmp_path):
    db = database(tmp_path)
    assert absences.balance(POLICY, 10)['remaining'] == 20
    with db.transaction() as connection:
        record = absences.create(connection, CID, absence(), OWNER, policy=POLICY)
        code, status = code_of(lambda: absences.create(
            connection, CID, absence(ref='otra'), OWNER,
            existing=[record], policy=POLICY))
        assert (code, status) == ('overlapping_absence', 409)
        code, status = code_of(lambda: absences.decide(
            connection, CID, record, OWNER, approve=True))
        assert (code, status) == ('separation_of_duties', 403)
        decided = absences.decide(connection, CID, record, REVIEWER, approve=True, note='ok')
    assert decided['state'] == 'approved'
    assert [step['action'] for step in decided['history']] == ['requested', 'approved']


def test_absence_revocation_keeps_history_and_hides_reason():
    record = {'requested_by': 'ana', 'state': 'approved', 'reason': 'médico',
              'history': [], 'ref': 'a1', 'employee_ref': 'e1'}
    assert absences.visible(record, viewer_id='otro', privileged=False)['reason'] == ''
    detail = code_of(lambda: absences.revoke(None, CID, dict(record), OWNER, reason=''))
    assert detail[0] == 'reason_required'


def test_shifts_reject_overlap_and_short_rest():
    plan = [
        {'employee_ref': 'e1', 'starts_at': '2026-10-05T08:00:00+02:00',
         'ends_at': '2026-10-05T16:00:00+02:00'},
        {'employee_ref': 'e1', 'starts_at': '2026-10-05T15:00:00+02:00',
         'ends_at': '2026-10-05T23:00:00+02:00'},
        {'employee_ref': 'e2', 'starts_at': '2026-10-05T08:00:00+02:00',
         'ends_at': '2026-10-05T16:00:00+02:00'},
        {'employee_ref': 'e2', 'starts_at': '2026-10-05T22:00:00+02:00',
         'ends_at': '2026-10-06T02:00:00+02:00'},
    ]
    codes = {problem['code'] for problem in shifts.validate(plan)}
    assert codes == {'overlap', 'rest_below_minimum'}


def test_shifts_need_coverage_and_a_note_to_publish(tmp_path):
    db = database(tmp_path)
    plan = [{'employee_ref': 'e1', 'starts_at': '2026-10-05T08:00:00+02:00',
             'ends_at': '2026-10-05T16:00:00+02:00'}]
    with db.transaction() as connection:
        assert code_of(lambda: shifts.publish(connection, CID, period='2026-10', plan=plan,
                                              required={'2026-10-05': 2}, actor=OWNER,
                                              note='publicación semanal'))[0] == 'coverage_gap'
        assert code_of(lambda: shifts.publish(connection, CID, period='2026-10', plan=plan,
                                              required={'2026-10-05': 1}, actor=OWNER,
                                              note=''))[0] == 'reason_required'
        published = shifts.publish(connection, CID, period='2026-10', plan=plan,
                                   required={'2026-10-05': 1}, actor=OWNER,
                                   note='publicación semanal revisada')
    assert published['coverage']['2026-10-05']['missing'] == 0


def test_onboarding_is_idempotent_and_closes_only_when_complete(tmp_path):
    db = database(tmp_path)
    with db.transaction() as connection:
        first, created = onboarding.open_case(connection, CID, employee_ref='e1',
                                              kind='onboarding', actor=OWNER,
                                              tasks=['contrato', 'accesos'])
        again, created_again = onboarding.open_case(connection, CID, employee_ref='e1',
                                                    kind='onboarding', actor=OWNER,
                                                    tasks=['contrato', 'accesos'])
        assert created is True and created_again is False
        assert first['id'] == again['id']
        onboarding.complete_task(connection, CID, first, name='contrato', actor=OWNER)
        assert onboarding.blockers(first) == ['accesos']
        closed = onboarding.complete_task(connection, CID, first, name='accesos', actor=OWNER)
        stored = json.loads(connection.execute('SELECT body FROM objects WHERE kind=?',
                                              ('rrhh_case',)).fetchone()['body'])
    assert closed['state'] == 'closed'
    assert stored['state'] == 'closed'


def test_documents_expire_and_conflict_after_signature(tmp_path):
    db = database(tmp_path)
    with db.transaction() as connection:
        record = documents.register(connection, CID, employee_ref='e1', kind='contrato',
                                    version='v1', expires_at='2020-01-01',
                                    requires_signature=True, actor=OWNER)
        assert code_of(lambda: documents.serve(record))[0] == 'document_expired'
        documents.request_signature(connection, CID, record, actor=OWNER)
        code, status = code_of(lambda: documents.replace_version(
            connection, CID, record, version='v2', actor=OWNER))
        assert (code, status) == ('signature_conflict', 409)
        assert record['state'] == 'signature_conflict'


def test_documents_read_receipt_is_idempotent(tmp_path):
    db = database(tmp_path)
    with db.transaction() as connection:
        record = documents.register(connection, CID, employee_ref='e1', kind='nomina',
                                    version='v1', actor=OWNER)
        documents.mark_read(connection, CID, record, reader_id='e1')
        documents.mark_read(connection, CID, record, reader_id='e1')
    assert record['read_by'] == ['e1']


def closure():
    return {'period': '2026-10',
            'result': {'content_hash': 'c' * 12, 'period': '2026-10',
                       'employees': {'e1': {'minutes': 465, 'hours': '7.75'}},
                       'issues': [], 'totals': {'employees': 1, 'minutes': 465, 'issues': 0}}}


def test_payroll_export_requires_provider_and_matching_approval(tmp_path):
    db = database(tmp_path)
    approval = {'id': 'ap1', 'result_hash': 'c' * 12}
    assert code_of(lambda: payroll.build(closure(), approval, provider=''))[0] == 'capability_unavailable'
    assert code_of(lambda: payroll.build(closure(), {'id': 'ap2', 'result_hash': 'd' * 12},
                                         provider='proveedor'))[0] == 'approval_stale'
    document = payroll.build(closure(), approval, provider='proveedor')
    assert document['format'] == payroll.FORMAT
    assert document['totals'] == {'employees': 1, 'minutes': 465}
    with db.transaction() as connection:
        code, status = code_of(lambda: payroll.record_ack(
            connection, CID, document, ref='R1', totals={'employees': 1, 'minutes': 400}))
        assert (code, status) == ('payroll_mismatch', 409)
        ack = payroll.record_ack(connection, CID, document, ref='R1',
                                 totals={'employees': 1, 'minutes': 465})
    assert ack['state'] == 'reconciled'


def test_payroll_reexport_needs_a_reason():
    document = payroll.build(closure(), {'id': 'ap1', 'result_hash': 'c' * 12},
                             provider='proveedor')
    assert code_of(lambda: payroll.reexport(None, CID, document, reason=''))[0] == 'reason_required'
    assert payroll.reexport(None, CID, document, reason='reenvío tras caída')['key'].startswith('payroll:')
