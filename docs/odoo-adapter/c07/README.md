# C07 · Transporte JSON-2

Estado de implementación: código entregado por lote a petición del propietario. Estado del gate: **NOT VERIFIED (gate integral requiere entorno real)**.

## Resultado

Allowlist de pares, IP fijada/SNI, sin redirect/proxy heredado, límites, retries solo lecturas, breaker y errores sanitizados.

Archivos principales: `agntia_gestoria/integrations/odoo/transport.py`. Endpoints y DTOs completos: [contratos](../contracts.md). Ownership/arquitectura: [architecture.md](../architecture.md).

## Invariantes

No tocar agente, producción, secretos reales ni fórmulas fiscales. Cada acceso remoto valida principal/empresa/tenant/conexión/capacidad. Nunca auto-review, action_post, pagos o presentación. Incertidumbre bloquea reintento de escritura y exige conciliación.

## Siguiente validación

Contratos HTTP reales, errores Odoo, TLS del servidor aprobado y medición de pool/latencias.

Ver TESTS.md, EVIDENCE.md, RISKS.md y DECISIONS.md de esta campaña. La presencia del código no aprueba una instalación Odoo no ejecutada.
