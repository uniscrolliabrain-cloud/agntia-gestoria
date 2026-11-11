# C18 · API y SDK Hono

Estado de implementación: código entregado por lote a petición del propietario. Estado del gate: **NOT VERIFIED (gate integral requiere entorno real)**.

## Resultado

Rutas nominadas, 202 jobs, errores uniformes, DTOs/validación frontera y allowlist Hono exacta; exports antiguos conservados.

Archivos principales: `agntia_gestoria/integrations/odoo/routes.py`, `typescript/odoo.ts`, `typescript/odoo-routes.ts`, `typescript/types/odoo.d.ts`. Endpoints y DTOs completos: [contratos](../contracts.md). Ownership/arquitectura: [architecture.md](../architecture.md).

## Invariantes

No tocar agente, producción, secretos reales ni fórmulas fiscales. Cada acceso remoto valida principal/empresa/tenant/conexión/capacidad. Nunca auto-review, action_post, pagos o presentación. Incertidumbre bloquea reintento de escritura y exige conciliación.

## Siguiente validación

Contrato real Python/Node/Hono, navegador actual y build consumidor pnpm; no se modifica agente.

Ver TESTS.md, EVIDENCE.md, RISKS.md y DECISIONS.md de esta campaña. La presencia del código no aprueba una instalación Odoo no ejecutada.
