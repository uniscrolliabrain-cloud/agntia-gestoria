# C15 · Contactos write-back

Estado de implementación: código entregado por lote a petición del propietario. Estado del gate: **NOT VERIFIED (gate integral requiere entorno real)**.

## Resultado

Dry-run inmutable, aprobación humana firmada ligada a DB, expected_write_date, ejecución única por propuesta y lectura de ledger tras incertidumbre.

Archivos principales: `agntia_gestoria/integrations/odoo/commands.py`, `infra/odoo/addons/agntia_bridge/models/bridge.py`. Endpoints y DTOs completos: [contratos](../contracts.md). Ownership/arquitectura: [architecture.md](../architecture.md).

## Invariantes

No tocar agente, producción, secretos reales ni fórmulas fiscales. Cada acceso remoto valida principal/empresa/tenant/conexión/capacidad. Nunca auto-review, action_post, pagos o presentación. Incertidumbre bloquea reintento de escritura y exige conciliación.

## Siguiente validación

Actualización remota concurrente, timeout/rotación y replay reales con bot mínimo.

Ver TESTS.md, EVIDENCE.md, RISKS.md y DECISIONS.md de esta campaña. La presencia del código no aprueba una instalación Odoo no ejecutada.
