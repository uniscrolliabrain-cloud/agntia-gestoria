# C03 · Laboratorio reproducible

Estado de implementación: código entregado por lote a petición del propietario. Estado del gate: **NOT VERIFIED (gate integral requiere entorno real)**.

## Resultado

Imagen fuente fijada, Postgres fijado, red interna, dos DB, bots separados, fixtures y backup/restore restringido al laboratorio.

Archivos principales: `infra/odoo/compose.yaml`, `infra/odoo/Dockerfile`, `scripts/odoo_bootstrap.py`, `scripts/odoo_fixture.py`, `scripts/odoo_backup.py`. Endpoints y DTOs completos: [contratos](../contracts.md). Ownership/arquitectura: [architecture.md](../architecture.md).

## Invariantes

No tocar agente, producción, secretos reales ni fórmulas fiscales. Cada acceso remoto valida principal/empresa/tenant/conexión/capacidad. Nunca auto-review, action_post, pagos o presentación. Incertidumbre bloquea reintento de escritura y exige conciliación.

## Siguiente validación

Construir, arrancar ambas DB, inspeccionar módulos/grupos, backup/restore y conexión cruzada reales.

Ver TESTS.md, EVIDENCE.md, RISKS.md y DECISIONS.md de esta campaña. La presencia del código no aprueba una instalación Odoo no ejecutada.
