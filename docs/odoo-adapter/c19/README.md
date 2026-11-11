# C19 · Herramientas, eventos y rota

Estado de implementación: código entregado por lote a petición del propietario. Estado del gate: **NOT VERIFIED (gate integral requiere entorno real)**.

## Resultado

Herramientas lectura/propuesta sin approve/commit, outbox/inbox/ACK y briefing basado en registros persistidos; contrato de rotas, sin scheduler paralelo.

Archivos principales: `typescript/odoo-agent-tools.ts`, `docs/odoo-adapter/agent-integration.md`. Endpoints y DTOs completos: [contratos](../contracts.md). Ownership/arquitectura: [architecture.md](../architecture.md).

## Invariantes

No tocar agente, producción, secretos reales ni fórmulas fiscales. Cada acceso remoto valida principal/empresa/tenant/conexión/capacidad. Nunca auto-review, action_post, pagos o presentación. Incertidumbre bloquea reintento de escritura y exige conciliación.

## Siguiente validación

Wiring AgntiaPro solo con aprobación; verificar gateway/event bus/policy/approval service y deduplicación del consumidor.

Ver TESTS.md, EVIDENCE.md, RISKS.md y DECISIONS.md de esta campaña. La presencia del código no aprueba una instalación Odoo no ejecutada.
