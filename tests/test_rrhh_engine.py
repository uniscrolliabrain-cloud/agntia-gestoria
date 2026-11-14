import pytest

from agntia_gestoria.integrations.errors import IntegrationError
from agntia_gestoria.integrations.rrhh import engine, snapshot
from agntia_gestoria.storage import Database, canonical

CID = 'a' * 32
OTHER = 'b' * 32
POLICY = {'policy_hash': 'p' * 10, 'jornada_diaria_horas_max': 9, 'holidays': ['2026-10-12']}


def database(tmp_path):
    db = Database(str(tmp_path))
    with db.transaction() as connection:
        connection.execute('INSERT INTO companies(id,body) VALUES(?,?)',
                           (CID, canonical({'id': CID, 'name': 'Uno'})))
        connection.execute('INSERT INTO companies(id,body) VALUES(?,?)',
                           (OTHER, canonical({'id': OTHER, 'name': 'Dos'})))
    return db


def employee(ref, punches=(), absences=()):
    return {'ref': ref, 'punches': list(punches), 'absences': list(absences)}


def punch(at, direction):
    return {'at': at, 'direction': direction}


def test_snapshot_is_stable_and_idempotent(tmp_path):
    db = database(tmp_path)

    def read():
        return {'marker': 'v1', 'sources': {'employees': []}}

    with db.transaction() as connection:
        first, created = snapshot.persist_snapshot(connection, CID, '2026-10', read,
                                                   policy_hash='p' * 10, timezone='Europe/Madrid')
        again, created_again = snapshot.persist_snapshot(connection, CID, '2026-10', read,
                                                         policy_hash='p' * 10, timezone='Europe/Madrid')
    assert created is True and created_again is False
    assert first['content_hash'] == again['content_hash']
    assert first['id'] == again['id']


def test_source_change_blocks_the_snapshot(tmp_path):
    db = database(tmp_path)
    calls = {'n': 0}

    def read():
        calls['n'] += 1
        return {'marker': 'v1' if calls['n'] == 1 else 'v2', 'sources': {}}

    with db.transaction() as connection:
        with pytest.raises(IntegrationError) as error:
            snapshot.persist_snapshot(connection, CID, '2026-10', read,
                                      policy_hash='p' * 10, timezone='Europe/Madrid')
    assert error.value.code == 'source_changed'
    assert error.value.status == 409


def test_tampered_snapshot_is_rejected():
    body = snapshot.snapshot_body(CID, '2026-10', {'employees': []},
                                  policy_hash='p' * 10, timezone='Europe/Madrid')
    body['sources'] = {'employees': [employee('intruso')]}
    with pytest.raises(IntegrationError) as error:
        snapshot.verify_snapshot(body)
    assert error.value.code == 'integrity'


def close(*employees, policy=None):
    merged = dict(POLICY if policy is None else policy)
    snap = {'period': '2026-10', 'content_hash': 'a' * 8, 'employees': list(employees),
            'policy_hash': merged['policy_hash']}
    return engine.close_period(snap, merged)


def test_normal_day_counts_minutes_and_the_legal_break():
    result = close(employee('e1', [punch('2026-10-05T08:00:00+02:00', 'in'),
                                   punch('2026-10-05T16:00:00+02:00', 'out')]))
    # 8 h continuadas: se descuenta la pausa de 15 minutos del art. 34.4 ET
    assert result['employees']['e1']['minutes'] == 480 - 15
    assert result['issues'] == []


def test_interval_over_six_hours_deducts_the_break():
    result = close(employee('e1', [punch('2026-10-05T08:00:00+02:00', 'in'),
                                   punch('2026-10-05T15:00:00+02:00', 'out')]))
    assert result['employees']['e1']['minutes'] == 420 - 15


def test_midnight_crossing_is_detected_not_imputed():
    result = close(employee('e1', [punch('2026-10-05T22:00:00+02:00', 'in'),
                                   punch('2026-10-06T06:00:00+02:00', 'out')]))
    assert result['employees']['e1']['minutes'] == 480 - 15
    assert any(issue['code'] == 'crosses_midnight' for issue in result['issues'])


def test_daylight_saving_change_uses_absolute_time():
    result = close(employee('e1', [punch('2026-10-24T22:00:00+02:00', 'in'),
                                   punch('2026-10-25T06:00:00+01:00', 'out')]))
    assert result['employees']['e1']['minutes'] == 540 - 15


def test_incomplete_and_duplicate_punches_are_issues():
    result = close(employee('e1', [punch('2026-10-05T08:00:00+02:00', 'in'),
                                   punch('2026-10-05T09:00:00+02:00', 'in'),
                                   punch('2026-10-05T17:00:00+02:00', 'out')]))
    codes = [issue['code'] for issue in result['issues']]
    assert 'duplicate_punch' in codes


def test_pending_absence_is_an_issue_and_approved_is_not():
    pending = employee('e1', [punch('2026-10-05T08:00:00+02:00', 'in'),
                              punch('2026-10-05T16:00:00+02:00', 'out')],
                       [{'starts_at': '2026-10-06T00:00:00+02:00',
                         'ends_at': '2026-10-07T00:00:00+02:00', 'state': 'pending'}])
    approved = employee('e2', [punch('2026-10-05T08:00:00+02:00', 'in'),
                               punch('2026-10-05T16:00:00+02:00', 'out')],
                        [{'starts_at': '2026-10-06T00:00:00+02:00',
                          'ends_at': '2026-10-07T00:00:00+02:00', 'state': 'approved'}])
    result = close(pending, approved)
    codes = [(issue['code'], issue['employee_ref']) for issue in result['issues']]
    assert ('pending_absence', 'e1') in codes
    assert all(ref != 'e2' for _, ref in codes)


def test_replay_is_identical_and_policy_change_alters_the_hash():
    first = close(employee('e1', [punch('2026-10-05T08:00:00+02:00', 'in'),
                                  punch('2026-10-05T16:00:00+02:00', 'out')]))
    second = close(employee('e1', [punch('2026-10-05T08:00:00+02:00', 'in'),
                                   punch('2026-10-05T16:00:00+02:00', 'out')]))
    other = close(employee('e1', [punch('2026-10-05T08:00:00+02:00', 'in'),
                                  punch('2026-10-05T16:00:00+02:00', 'out')]),
                  policy={**POLICY, 'policy_hash': 'q' * 10})
    assert engine.replay(first) == engine.replay(second)
    assert engine.replay(first) != engine.replay(other)


def test_transitions_require_actor_reason_and_evidence():
    assert engine.transition('prepared', 'pending_review', 'owner', 'listo', 'snap-1')['to'] == 'pending_review'
    with pytest.raises(ValueError):
        engine.transition('prepared', 'exported', 'owner', 'salto', 'snap-1')
    with pytest.raises(ValueError):
        engine.transition('prepared', 'pending_review', '', 'sin actor', 'snap-1')
