# C06 · Conexiones y secretos

Estado de implementación: código entregado por lote a petición del propietario. Estado del gate: **NOT VERIFIED (gate integral requiere entorno real)**.

## Resultado

Registro servidor con refs de entorno, scopes, HTTPS/CIDR, rechazo URL arbitraria, binding explícito y revocación.

Archivos principales: `agntia_gestoria/integrations/registry.py`, `agntia_gestoria/integrations/policy.py`, `agntia_gestoria/integrations/odoo/service.py`. Endpoints y DTOs completos: [contratos](../contracts.md). Ownership/arquitectura: [architecture.md](../architecture.md).

## Invariantes

No tocar agente, producción, secretos reales ni fórmulas fiscales. Cada acceso remoto valida principal/empresa/tenant/conexión/capacidad. Nunca auto-review, action_post, pagos o presentación. Incertidumbre bloquea reintento de escritura y exige conciliación.

## Siguiente validación

Rotación real por DB, DNS/TLS y demostración de mínimos permisos del bot.

Ver TESTS.md, EVIDENCE.md, RISKS.md y DECISIONS.md de esta campaña. La presencia del código no aprueba una instalación Odoo no ejecutada.
