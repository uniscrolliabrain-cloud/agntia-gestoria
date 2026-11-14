"""Salud del módulo: sin credenciales, sin secretos y con causa.

Distingue «no configurado» de «caído» y de «snapshot viejo». Un estado global
`ok` con un proveedor caído sería mentira, así que el estado se degrada.
"""
from datetime import datetime, timezone

STALE_SECONDS = 86400


def _age(cutoff_at, now=None):
    if not cutoff_at:
        return None
    reference = now or datetime.now(timezone.utc)
    moment = datetime.fromisoformat(cutoff_at)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return max(0, int((reference - moment).total_seconds()))


def build(*, enabled, provider_state='not_configured', snapshot_cutoff=None,
          orphans=0, now=None):
    if not enabled:
        return {'module': 'rrhh', 'status': 'disabled', 'reason': 'Sin bandera para la empresa'}
    age = _age(snapshot_cutoff, now)
    checks = {
        'provider': provider_state,
        'snapshot': 'missing' if age is None else ('stale' if age > STALE_SECONDS else 'fresh'),
        'orphans': orphans,
    }
    if provider_state == 'down':
        status = 'degraded'
        reason = 'El proveedor no responde'
    elif orphans:
        status = 'degraded'
        reason = f'{orphans} trabajos huérfanos sin barrido'
    elif age is None:
        status = 'starting'
        reason = 'Todavía no hay snapshot del periodo'
    elif age > STALE_SECONDS:
        status = 'degraded'
        reason = 'El snapshot tiene más de un día'
    else:
        status = 'ok'
        reason = 'Sin incidencias conocidas'
    return {'module': 'rrhh', 'status': status, 'reason': reason,
            'checks': checks, 'snapshot_age_seconds': age}
