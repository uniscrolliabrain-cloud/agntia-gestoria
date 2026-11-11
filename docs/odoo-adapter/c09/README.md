# C09 · Binding y aislamiento

Estado de implementación: código entregado por lote a petición del propietario. Estado del gate: **NOT VERIFIED (gate integral requiere entorno real)**.

## Resultado

Empresa/tenant/conexión/UUID DB/remote company explícitos; confirmación fiscal humana cuando falta identidad, scopes antes de cada HTTP.

Archivos principales: `agntia_gestoria/integrations/odoo/service.py`, `agntia_gestoria/integrations/policy.py`. Endpoints y DTOs completos: [contratos](../contracts.md). Ownership/arquitectura: [architecture.md](../architecture.md).

## Invariantes

No tocar agente, producción, secretos reales ni fórmulas fiscales. Cada acceso remoto valida principal/empresa/tenant/conexión/capacidad. Nunca auto-review, action_post, pagos o presentación. Incertidumbre bloquea reintento de escritura y exige conciliación.

## Siguiente validación

E2E de dos bases con credenciales intercambiadas, mismos nombres, varios humanos y agentes.

Ver TESTS.md, EVIDENCE.md, RISKS.md y DECISIONS.md de esta campaña. La presencia del código no aprueba una instalación Odoo no ejecutada.
