# C13 · Sync incremental y reconciliación

Estado de implementación: código entregado por lote a petición del propietario. Estado del gate: **NOT VERIFIED (gate integral requiere entorno real)**.

## Resultado

Cursor write_date con overlap, escaneo por id y watermark tras commit, missing en fullscan, leases/heartbeats/retries y dead-letter por estado bloqueado.

Archivos principales: `agntia_gestoria/integrations/odoo/imports.py`, `agntia_gestoria/integrations/odoo/jobs.py`. Endpoints y DTOs completos: [contratos](../contracts.md). Ownership/arquitectura: [architecture.md](../architecture.md).

## Invariantes

No tocar agente, producción, secretos reales ni fórmulas fiscales. Cada acceso remoto valida principal/empresa/tenant/conexión/capacidad. Nunca auto-review, action_post, pagos o presentación. Incertidumbre bloquea reintento de escritura y exige conciliación.

## Siguiente validación

Crash real fetch/commit/ack, modificación concurrente, avance de cursores sin pérdidas y re-sync completo.

Ver TESTS.md, EVIDENCE.md, RISKS.md y DECISIONS.md de esta campaña. La presencia del código no aprueba una instalación Odoo no ejecutada.
