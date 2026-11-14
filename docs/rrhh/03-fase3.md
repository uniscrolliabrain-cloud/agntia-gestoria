# Fase 3 · Odoo laboral, importación e incidencias

Objetivo: que el cierre se alimente de datos reales de Odoo (o de su doble) con frescura demostrable y conflictos explícitos.

## Etapa 3.1 · Addons laborales, descubrimiento y fixtures

- **Nuevos:** `infra/odoo/addons/agntia_hr/__manifest__.py`, `models/hr_bridge.py`, `security/ir.model.access.csv`, `docs/odoo-adapter/rrhh-addons.md`, `scripts/odoo_hr_bootstrap.py`, `tests/integration/test_odoo_hr_live.py`.
- **Tocados:** `infra/odoo/upstream-lock.json` (SHA de `hr`, `hr_attendance`, `hr_holidays`), `integrations/odoo/discovery.py` (capacidades `hr.*`).
- **Reglas:** instalación por lista cerrada, manifiesto y licencia verificados contra el SHA del laboratorio, superusuario prohibido igual que en el bridge actual; si falta un addon, la capacidad se declara no disponible y el resto degrada.
- **Tests:** instalación limpia, empresa con `hr_holidays` ausente, lectura de empleados sin permiso de escritura, comprobación de que el addon no expone ORM genérico.
- **Aceptación:** `odoo_hr_bootstrap.py` deja un run reproducible con SHA de imagen, Odoo y addons; sin laboratorio, la suite real se salta igual que hoy y se declara BLOCKED.

## Etapa 3.2 · Importación incremental con frescura y conflicto

- **Nuevos:** `integrations/rrhh/imports.py`, `tests/test_rrhh_imports.py`, `tests/fixtures/rrhh/imports/*.json`.
- **Tocados:** `integrations/rrhh/routes.py` (`POST .../rrhh/imports`), `integrations/errors.py` (`stale_cursor`, `scope_violation`).
- **Reglas:** cursor por `(write_date, id)` con comparación tipada, no texto; revalidación dentro de la transacción; empleado con empresa vacía se rechaza con `scope_violation`; reentrega idempotente por `event_id`.
- **Tests:** 1.100 empleados y 5.000 fichajes paginados sin pérdida; mismo `write_date` en 250 registros; cursor caducado; dos importaciones concurrentes dejan un solo hecho.
- **Aceptación:** dos ejecuciones seguidas sin cambios no importan nada y lo reportan.

## Etapa 3.3 · Incidencias y conciliación sin efectos silenciosos

- **Nuevos:** `integrations/rrhh/issues.py`, `reconcile.py`, `tests/test_rrhh_issues.py`, `tests/test_rrhh_reconcile.py`.
- **Tocados:** `integrations/rrhh/routes.py` (`GET .../rrhh/issues`, `POST .../rrhh/issues/{id}/propose`), `jobs.py` (trabajo técnico de conciliación).
- **Reglas:** una incidencia explica el motivo y el dato original; proponer corrección no escribe en Odoo; sólo una aprobación con rol y hash habilita efecto; reconciliación consulta la identidad persistida antes de repetir.
- **Tests:** fichaje duplicado, fichaje incompleto, ausencia pendiente frente a aprobada, ACK perdido, dos reconciliaciones simultáneas (un solo efecto).
- **Aceptación:** ninguna incidencia se cierra sin actor, motivo y evidencia.
