"""Panel de seguimiento: frescura, evidencia y tareas por vencimiento.

Un informe sin fecha de corte no sirve para decidir. Aquí cada cifra viaja con
su snapshot, su política y cuánto tiempo hace que se leyó el origen.
"""
from datetime import datetime, timezone

from . import issues as issue_catalogue


def _age_seconds(cutoff_at, now=None):
    reference = now or datetime.now(timezone.utc)
    moment = datetime.fromisoformat(cutoff_at)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return max(0, int((reference - moment).total_seconds()))


def dashboard(closure, *, snapshot_cutoff, policy_version, provider_state='not_configured',
              now=None):
    result = closure['result']
    summary = issue_catalogue.summarize(result['issues'])
    return {
        'period': result['period'],
        'totals': result['totals'],
        'policy': {'hash': result['policy_hash'], 'version': policy_version},
        'snapshot': {'hash': result['snapshot_hash'], 'cutoff_at': snapshot_cutoff,
                     'age_seconds': _age_seconds(snapshot_cutoff, now)},
        'provider': provider_state,
        'issues': summary,
        'blocking': [item['code'] for item in summary if item['severity'] in ('critical', 'high')],
        'evidence': ['snapshot inmutable', 'política compilada', 'auditoría encadenada'],
    }


def proactive_tasks(closure, *, due_days=2):
    """Lo que hay que resolver antes de exportar, con su fecha límite."""
    tasks = []
    for item in issue_catalogue.actionable(closure['result']['issues']):
        tasks.append({'code': item['code'], 'employee_ref': item['employee_ref'],
                      'next_action': item['next_action'], 'due_in_days': due_days})
    return sorted(tasks, key=lambda task: (task['code'], task['employee_ref']))


def freshness_warning(age_seconds, *, threshold_seconds=86400):
    return {'stale': age_seconds > threshold_seconds, 'age_seconds': age_seconds,
            'threshold_seconds': threshold_seconds}
