# C05 · Migración aditiva

Estado de implementación: código entregado por lote a petición del propietario. Estado del gate: **NOT VERIFIED (gate integral requiere entorno real)**.

## Resultado

Backup SQLite antes de DDL, transacción, tablas e índices de empresa, unicidad de claves/propuestas, rollback en fallo.

Archivos principales: `agntia_gestoria/integrations/migrations.py`. Endpoints y DTOs completos: [contratos](../contracts.md). Ownership/arquitectura: [architecture.md](../architecture.md).

## Invariantes

No tocar agente, producción, secretos reales ni fórmulas fiscales. Cada acceso remoto valida principal/empresa/tenant/conexión/capacidad. Nunca auto-review, action_post, pagos o presentación. Incertidumbre bloquea reintento de escritura y exige conciliación.

## Siguiente validación

Ensayar restauración WAL y copia representativa anterior fuera de datos reales, medir concurrencia y disco.

Ver TESTS.md, EVIDENCE.md, RISKS.md y DECISIONS.md de esta campaña. La presencia del código no aprueba una instalación Odoo no ejecutada.
