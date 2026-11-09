# C17 · Bridge transaccional

Estado de implementación: código entregado por lote a petición del propietario. Estado del gate: **NOT VERIFIED (gate integral requiere entorno real)**.

## Resultado

Addons propios LGPL3: UUID DB, snapshots, ledger único, advisory lock, firma HMAC, ACL y guardas Python no falsificables por JSON.

Archivos principales: `infra/odoo/addons/agntia_bridge`, `infra/odoo/addons/agntia_bridge_account`. Endpoints y DTOs completos: [contratos](../contracts.md). Ownership/arquitectura: [architecture.md](../architecture.md).

## Invariantes

No tocar agente, producción, secretos reales ni fórmulas fiscales. Cada acceso remoto valida principal/empresa/tenant/conexión/capacidad. Nunca auto-review, action_post, pagos o presentación. Incertidumbre bloquea reintento de escritura y exige conciliación.

## Siguiente validación

Instalación ORM/ACL real, dos solicitudes simultáneas y comportamiento de aislamiento/retry PostgreSQL. No afirmar que está instalado.

Ver TESTS.md, EVIDENCE.md, RISKS.md y DECISIONS.md de esta campaña. La presencia del código no aprueba una instalación Odoo no ejecutada.
