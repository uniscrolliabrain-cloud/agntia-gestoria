# C11 · Facturas sin doble cómputo

Estado de implementación: código entregado por lote a petición del propietario. Estado del gate: **NOT VERIFIED (gate integral requiere entorno real)**.

## Resultado

Snapshot atómico bridge de invoice_line_ids, cuatro tipos, EUR, reconciliación de totales, refunds firmados, bloqueo de impuestos compuestos/ambigüedad.

Archivos principales: `agntia_gestoria/integrations/odoo/mappers/invoice.py`, `agntia_gestoria/integrations/odoo/reads.py`. Endpoints y DTOs completos: [contratos](../contracts.md). Ownership/arquitectura: [architecture.md](../architecture.md).

## Invariantes

No tocar agente, producción, secretos reales ni fórmulas fiscales. Cada acceso remoto valida principal/empresa/tenant/conexión/capacidad. Nunca auto-review, action_post, pagos o presentación. Incertidumbre bloquea reintento de escritura y exige conciliación.

## Siguiente validación

Fixtures reales 0/4/10/21, exento, retención, redondeos y monedas; los no soportados deben bloquear, no inventar clasificación.

Ver TESTS.md, EVIDENCE.md, RISKS.md y DECISIONS.md de esta campaña. La presencia del código no aprueba una instalación Odoo no ejecutada.
