from datetime import date, datetime, timezone

import pytest

from agntia_gestoria.integrations.errors import IntegrationError
from agntia_gestoria.integrations.rrhh import (health, metrics, permissions, reports,
                                               resilience, retention)

NOW = datetime(2026, 11, 12, 12, 0, tzinfo=timezone.utc)


def closure(*issues):
    return {'period': '2026-10', 'result': {
        'period': '2026-10', 'policy_hash': 'p' * 10, 'snapshot_hash': 's' * 8,
        'content_hash': 'c' * 12,
        'employees': {'e1': {'minutes': 465, 'hours': '7.75'}},
        'issues': list(issues),
        'totals': {'employees': 1, 'minutes': 465, 'issues': len(issues)}}}


def issue(code, severity='high'):
    return {'code': code, 'employee_ref': 'e1', 'at': '2026-10-05', 'detail': 'd',
            'severity': severity, 'base_legal': 'art. 34.9 ET',
            'next_action': 'Revisar'}


def test_dashboard_reports_freshness_and_blocking_issues():
    report = reports.dashboard(closure(issue('incomplete_punch')),
                               snapshot_cutoff='2026-11-12T10:00:00+00:00',
                               policy_version='2026-11', now=NOW)
    assert report['snapshot']['age_seconds'] == 7200
    assert report['blocking'] == ['incomplete_punch']
    assert report['evidence']
    assert reports.freshness_warning(report['snapshot']['age_seconds'])['stale'] is False
    assert reports.proactive_tasks(closure(issue('incomplete_punch')))[0]['due_in_days'] == 2


def test_metrics_compute_percentiles_without_leaking_data():
    collector = metrics.Metrics()
    for value in (10, 20, 30, 40, 100):
        collector.observe('rrhh.closure.prepare', 'ok', value)
    collector.observe('rrhh.closure.prepare', 'error', 500)
    snapshot = collector.snapshot()
    capability = snapshot['capabilities']['rrhh.closure.prepare']
    assert capability['counts'] == {'ok': 5, 'error': 1}
    assert capability['p50_ms'] == 30
    assert capability['p95_ms'] == 500
    with pytest.raises(ValueError):
        collector.observe('x', 'raro', 1)


def test_health_degrades_with_provider_orphans_or_stale_snapshot():
    assert health.build(enabled=False)['status'] == 'disabled'
    assert health.build(enabled=True, snapshot_cutoff=None)['status'] == 'starting'
    assert health.build(enabled=True, provider_state='down',
                        snapshot_cutoff='2026-11-12T11:00:00+00:00', now=NOW)['status'] == 'degraded'
    assert health.build(enabled=True, orphans=2,
                        snapshot_cutoff='2026-11-12T11:00:00+00:00', now=NOW)['status'] == 'degraded'
    assert health.build(enabled=True, snapshot_cutoff='2026-11-10T11:00:00+00:00',
                        now=NOW)['status'] == 'degraded'
    assert health.build(enabled=True, snapshot_cutoff='2026-11-12T11:00:00+00:00',
                        now=NOW)['status'] == 'ok'


def test_breaker_opens_half_opens_and_recovers():
    clock = {'now': 0.0}
    breaker = resilience.Breaker(threshold=2, cooldown=30, clock=lambda: clock['now'])

    def boom():
        raise RuntimeError('proveedor caído')

    for _ in range(2):
        with pytest.raises(RuntimeError):
            breaker.call(boom)
    assert breaker.state == 'open'
    with pytest.raises(IntegrationError) as error:
        breaker.call(lambda: 'no debería llegar')
    assert error.value.code == 'provider_unavailable' and error.value.retryable is True
    clock['now'] = 31
    assert breaker.state == 'half_open'
    assert breaker.call(lambda: 'ok') == 'ok'
    assert breaker.state == 'closed'


def test_retry_after_is_bounded():
    assert resilience.retry_after_seconds('7') == 7
    assert resilience.retry_after_seconds('no-numérico') == 5
    assert resilience.retry_after_seconds('9999') == 120


def test_permission_matrix_denies_by_default_and_marks_sensitive():
    assert permissions.allowed('owner', 'cualquiera', 'api') is True
    assert permissions.allowed('agent', 'rrhh.closure.approve', 'api') is False
    denial = permissions.check('viewer', 'rrhh.write', 'sdk')
    assert denial['allowed'] is False and denial['reason']
    assert permissions.allowed('reviewer', 'rrhh.closure.approve', 'api') is True
    assert permissions.allowed('reviewer', 'rrhh.closure.approve', 'voice') is False
    assert permissions.sensitive('rrhh.closure.export') is True
    assert sorted(permissions.matrix_snapshot()) == ['agent', 'owner', 'reviewer', 'viewer']
    assert permissions.decrement_in_flight('agent', 'rrhh.closure.export', 'api') is False


def test_retention_purges_only_outside_the_window():
    records = [
        {'id': 'viejo', 'created_at': '2026-09-01T00:00:00+00:00'},
        {'id': 'nuevo', 'created_at': '2026-11-01T00:00:00+00:00'},
        {'id': 'vigente', 'created_at': '2026-09-01T00:00:00+00:00', 'legal_hold': True},
        {'id': 'sin-fecha'},
    ]
    plan = retention.purgeable(records, today=date(2026, 11, 12))
    assert plan['purge'] == ['viejo']
    assert plan['cutoff'] == '2026-10-01'
    result = retention.purge(records, today=date(2026, 11, 12))
    assert result == {'deleted': 1, 'kept': 3, 'plan': plan}


def test_backup_rotation_keeps_the_newest():
    backups = [{'at': f'2026-11-{day:02d}T00:00:00+00:00', 'path': f'b{day}', 'sha256': 'x'}
               for day in range(1, 11)]
    rotated = retention.rotation(backups, keep=3)
    assert [item['path'] for item in rotated['keep']] == ['b10', 'b9', 'b8']
    assert len(rotated['delete']) == 7
