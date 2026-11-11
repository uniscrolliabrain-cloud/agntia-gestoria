# C04 · Contratos tipados

Estado de implementación: código entregado por lote a petición del propietario. Estado del gate: **PASS (contratos locales; no acredita proveedor)**.

## Resultado

DTOs cerrados, Decimal string, IDs, hashes, esquemas y error público sanitizado.

Archivos principales: `agntia_gestoria/integrations/contracts.py`, `agntia_gestoria/integrations/errors.py`. Endpoints y DTOs completos: [contratos](../contracts.md). Ownership/arquitectura: [architecture.md](../architecture.md).

## Invariantes

No tocar agente, producción, secretos reales ni fórmulas fiscales. Cada acceso remoto valida principal/empresa/tenant/conexión/capacidad. Nunca auto-review, action_post, pagos o presentación. Incertidumbre bloquea reintento de escritura y exige conciliación.

## Siguiente validación

Ejecutar contratos de proveedor reales además de validación local; cotejar cliente/servidor con payloads capturados sin PII.

Ver TESTS.md, EVIDENCE.md, RISKS.md y DECISIONS.md de esta campaña. La presencia del código no aprueba una instalación Odoo no ejecutada.
