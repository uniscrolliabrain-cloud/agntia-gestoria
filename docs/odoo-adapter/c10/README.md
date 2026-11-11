# C10 · Contactos

Estado de implementación: código entregado por lote a petición del propietario. Estado del gate: **NOT VERIFIED (gate integral requiere entorno real)**.

## Resultado

Keyset id, páginas100, 1101 contactos en fixture de prueba, compañía estricta, Unicode y enlace por ID nunca por nombre.

Archivos principales: `agntia_gestoria/integrations/odoo/reads.py`, `agntia_gestoria/integrations/odoo/mappers/partner.py`. Endpoints y DTOs completos: [contratos](../contracts.md). Ownership/arquitectura: [architecture.md](../architecture.md).

## Invariantes

No tocar agente, producción, secretos reales ni fórmulas fiscales. Cada acceso remoto valida principal/empresa/tenant/conexión/capacidad. Nunca auto-review, action_post, pagos o presentación. Incertidumbre bloquea reintento de escritura y exige conciliación.

## Siguiente validación

Paginación Odoo real y reglas de contactos compartidos; compartidos sin company se excluyen deliberadamente.

Ver TESTS.md, EVIDENCE.md, RISKS.md y DECISIONS.md de esta campaña. La presencia del código no aprueba una instalación Odoo no ejecutada.
