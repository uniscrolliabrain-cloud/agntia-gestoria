# C20 · Hardening y entrega

Estado de implementación: código entregado por lote a petición del propietario. Estado del gate: **NOT VERIFIED (gate integral requiere entorno real)**.

## Resultado

Suite local, live A–E opt-in, backup/recovery scripts, CI normal y manual, runbooks y checklist de piloto.

Archivos principales: `tests/test_odoo_adapter.py`, `tests/test_odoo_hardening.py`, `tests/integration/test_odoo_live.py`, `.github/workflows/odoo-lab.yml`. Endpoints y DTOs completos: [contratos](../contracts.md). Ownership/arquitectura: [architecture.md](../architecture.md).

## Invariantes

No tocar agente, producción, secretos reales ni fórmulas fiscales. Cada acceso remoto valida principal/empresa/tenant/conexión/capacidad. Nunca auto-review, action_post, pagos o presentación. Incertidumbre bloquea reintento de escritura y exige conciliación.

## Siguiente validación

Ejecutar Docker/live/fallos/concurrencia/restauración/UI y aceptación; rendimiento/coste real aún no medidos.

Ver TESTS.md, EVIDENCE.md, RISKS.md y DECISIONS.md de esta campaña. La presencia del código no aprueba una instalación Odoo no ejecutada.
