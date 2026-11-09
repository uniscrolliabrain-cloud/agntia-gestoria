# C16 · Facturas borrador

Estado de implementación: código entregado por lote a petición del propietario. Estado del gate: **NOT VERIFIED (gate integral requiere entorno real)**.

## Resultado

Solo out_invoice EUR/borrador, IDs configurados, cotejo de totales, hash local, transacción remota y bloqueo de publicación.

Archivos principales: `agntia_gestoria/integrations/odoo/commands.py`, `infra/odoo/addons/agntia_bridge_account`. Endpoints y DTOs completos: [contratos](../contracts.md). Ownership/arquitectura: [architecture.md](../architecture.md).

## Invariantes

No tocar agente, producción, secretos reales ni fórmulas fiscales. Cada acceso remoto valida principal/empresa/tenant/conexión/capacidad. Nunca auto-review, action_post, pagos o presentación. Incertidumbre bloquea reintento de escritura y exige conciliación.

## Siguiente validación

Creación real con configuración contable19, fallo parcial/rollback, nombre no emitido y cero posted.

Ver TESTS.md, EVIDENCE.md, RISKS.md y DECISIONS.md de esta campaña. La presencia del código no aprueba una instalación Odoo no ejecutada.
