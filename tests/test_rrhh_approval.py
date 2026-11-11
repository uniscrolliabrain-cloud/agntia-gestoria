import pytest

from agntia_gestoria.auth import Actor
from agntia_gestoria.integrations.errors import IntegrationError
from agntia_gestoria.integrations.rrhh import approval, export
from agntia_gestoria.storage import Database, canonical

CID = 'a' * 32
PREPARER = 'ana-prep'
REVIEWER = Actor('luis-rev', 'reviewer', (CID,))
OWNER = Actor('marta-own', 'owner', ('*',))
VIEWER = Actor('vero-view', 'viewer', (CID,))


def database(tmp_path):
    db = Database(str(tmp_path))
    with db.transaction() as connection:
        connection.execute('INSERT INTO companies(id,body) VALUES(?,?)',
                           (CID, canonical({'id': CID, 'name': 'Uno'})))
    return db


def result_with(*issues):
    return {'period': '2026-10', 'policy_hash': 'p' * 10, 'snapshot_hash': 's' * 8,
            'content_hash': 'c' * 12,
            'employees': {'e1': {'minutes': 465, 'hours': '7.75', 'intervals': 1}},
            'issues': [{'code': code, 'employee_ref': 'e1', 'at': '2026-10-05',
                        'detail': 'd', 'base_legal': 'art. 34.9 ET'} for code in issues],
            'totals': {'employees': 1, 'minutes': 465, 'issues': len(issues)}}


def code_of(call):
    with pytest.raises(IntegrationError) as error:
        call()
    return error.value.code, error.value.status


def test_approval_is_bound_to_the_exact_result():
    result = result_with()
    record = approval.approve(result, REVIEWER, prepared_by=PREPARER,
                              justification='Revisados fichajes y pausas del periodo')
    assert record['result_hash'] == result['content_hash']
    assert record['snapshot_hash'] == result['snapshot_hash']
    assert approval.verify_approval(record, result)['approved_by'] == REVIEWER.id


def test_the_preparer_cannot_approve():
    result = result_with()
    code, status = code_of(lambda: approval.approve(
        result, Actor(PREPARER, 'reviewer', (CID,)), prepared_by=PREPARER,
        justification='Me lo apruebo yo mismo sin revisar nada'))
    assert (code, status) == ('separation_of_duties', 403)


def test_viewer_cannot_approve():
    code, status = code_of(lambda: approval.approve(
        result_with(), VIEWER, prepared_by=PREPARER,
        justification='Solo estoy mirando el cierre del mes'))
    assert (code, status) == ('forbidden', 403)


def test_justification_is_required():
    for value in ('', '   ', 'corto'):
        code, status = code_of(lambda: approval.approve(
            result_with(), REVIEWER, prepared_by=PREPARER, justification=value))
        assert (code, status) == ('justification_required', 422)


def test_unreviewed_issues_block_the_approval():
    code, status = code_of(lambda: approval.approve(
        result_with('crosses_midnight', 'pending_absence'), REVIEWER,
        prepared_by=PREPARER, justification='Revisado el cierre completo del mes'))
    assert (code, status) == ('unreviewed_issues', 409)


def test_each_issue_is_accepted_by_code():
    result = result_with('crosses_midnight', 'crosses_midnight')
    record = approval.approve(result, OWNER, prepared_by=PREPARER,
                              justification='Turno de noche: el corte es correcto',
                              accepted_issues=['crosses_midnight'])
    assert record['acknowledged'] == {'crosses_midnight': 2}
    code, status = code_of(lambda: approval.approve(
        result, OWNER, prepared_by=PREPARER, justification='Acepto lo que no hay',
        accepted_issues=['worked_on_holiday']))
    assert (code, status) == ('unknown_issue', 422)


def test_recalculation_invalidates_the_approval():
    result = result_with()
    record = approval.approve(result, REVIEWER, prepared_by=PREPARER,
                              justification='Cierre revisado antes de exportar')
    changed = dict(result, content_hash='d' * 12)
    code, status = code_of(lambda: approval.verify_approval(record, changed))
    assert (code, status) == ('approval_stale', 409)


def test_tampered_approval_is_rejected():
    result = result_with()
    record = approval.approve(result, REVIEWER, prepared_by=PREPARER,
                              justification='Aprobación legítima del cierre')
    record['approved_by'] = 'otra-persona'
    code, status = code_of(lambda: approval.verify_approval(record, result))
    assert (code, status) == ('integrity', 409)


def test_export_is_idempotent_and_keeps_one_record(tmp_path):
    db = database(tmp_path)
    result = result_with()
    record = approval.approve(result, REVIEWER, prepared_by=PREPARER,
                              justification='Todo revisado para exportar a nómina')
    with db.transaction() as connection:
        first, created = export.export_period(connection, CID, result, record, REVIEWER)
        again, created_again = export.export_period(connection, CID, result, record, REVIEWER)
        stored = connection.execute(
            'SELECT COUNT(*) AS total FROM objects WHERE company_id=? AND kind=?',
            (CID, export.KIND)).fetchone()['total']
    assert created is True and created_again is False
    assert stored == 1
    assert first['id'] == again['id']
    assert first['manifest']['totals'] == result['totals']
    assert first['manifest']['approval_id'] == record['id']


def test_export_requires_an_approval_for_that_result(tmp_path):
    db = database(tmp_path)
    result = result_with()
    record = approval.approve(result, REVIEWER, prepared_by=PREPARER,
                              justification='Cierre aprobado para su exportación')
    with db.transaction() as connection:
        code, status = code_of(lambda: export.export_period(
            connection, CID, dict(result, content_hash='e' * 12), record, REVIEWER))
    assert (code, status) == ('approval_stale', 409)


def test_viewer_cannot_export(tmp_path):
    db = database(tmp_path)
    result = result_with()
    record = approval.approve(result, REVIEWER, prepared_by=PREPARER,
                              justification='Aprobado y listo para exportar')
    with db.transaction() as connection:
        code, status = code_of(lambda: export.export_period(
            connection, CID, result, record, VIEWER))
    assert (code, status) == ('forbidden', 403)


def test_manifest_hash_survives_a_round_trip(tmp_path):
    db = database(tmp_path)
    result = result_with('pending_absence')
    record = approval.approve(result, OWNER, prepared_by=PREPARER,
                              justification='Ausencia pendiente aceptada por dirección',
                              accepted_issues=['pending_absence'])
    with db.transaction() as connection:
        body, _ = export.export_period(connection, CID, result, record, OWNER)
    assert export.verify_export(body)['manifest']['issues'] == {'pending_absence': 1}
    body['manifest']['totals']['minutes'] = 1
    code, _ = code_of(lambda: export.verify_export(body))
    assert code == 'integrity'
