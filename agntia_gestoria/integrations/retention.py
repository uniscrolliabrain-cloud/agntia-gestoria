"""Política de retención del ledger de operaciones (tarea 27 del handoff).

Una clave de idempotencia solo puede olvidarse cuando ya no queda ningún
camino que pueda reintentar o reconciliar la operación que identifica. La
ventana tiene que cubrir la ruta más lenta, no la habitual:

- el presupuesto de reintentos del worker,
- la retención de trabajos retrasados o en cuarentena,
- la antigüedad de backup que se acepta restaurar en un incidente,
- y un margen de seguridad para relojes, colas y restauraciones tardías.

Las claves caducadas no se borran ni se reactivan solas: pasan a revisión
manual, porque reactivar una clave antigua podría crear un segundo efecto
remoto sobre una operación que aún era reconciliable.
"""
from datetime import datetime,timedelta,timezone

# Valores predeterminados de revisión del ledger. Se conservan sus claves. Un cambio necesita
# una regresión que demuestre que la ventana sigue cubriendo la restauración
# de backup más lenta tolerada.
POLICY={
    'retry_budget_days':1,
    'delayed_job_days':7,
    'backup_restore_days':35,
    'safety_margin_days':7,
}

STATES=('reconcilable','expired_manual_review')


def retention_days(policy=None):
    values=policy or POLICY
    return max(values['retry_budget_days'],values['delayed_job_days'],values['backup_restore_days'])+values['safety_margin_days']


def retention_window(policy=None):
    return timedelta(days=retention_days(policy))


def _as_utc(value):
    if value.tzinfo is None:return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def classify(created_at,now=None,policy=None):
    """Devuelve el estado de la clave sin decidir por sí sola ningún reintento."""
    moment=_as_utc(now or datetime.now(timezone.utc))
    created=_as_utc(created_at if isinstance(created_at,datetime) else datetime.fromisoformat(str(created_at)))
    if created>moment+timedelta(minutes=5):raise ValueError('La clave no puede nacer en el futuro')
    if moment-created<=retention_window(policy):return 'reconcilable'
    return 'expired_manual_review'


def is_reconcilable(created_at,now=None,policy=None):
    return classify(created_at,now,policy)=='reconcilable'
