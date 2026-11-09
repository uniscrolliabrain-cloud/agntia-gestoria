# C14 · Adjuntos y originales

Estado de implementación: código entregado por lote a petición del propietario. Estado del gate: **NOT VERIFIED (gate integral requiere entorno real)**.

## Resultado

Metadatos iniciales, descarga explícita limitada, hash/sniff/scanner, original cifrado con Fernet y revisión no automática.

Archivos principales: `agntia_gestoria/integrations/odoo/attachments.py`, `agntia_gestoria/integrations/odoo/vault.py`. Endpoints y DTOs completos: [contratos](../contracts.md). Ownership/arquitectura: [architecture.md](../architecture.md).

## Invariantes

No tocar agente, producción, secretos reales ni fórmulas fiscales. Cada acceso remoto valida principal/empresa/tenant/conexión/capacidad. Nunca auto-review, action_post, pagos o presentación. Incertidumbre bloquea reintento de escritura y exige conciliación.

## Siguiente validación

Scanner real y archivos corruptos/maliciosos, permisos NTFS, backups de claves y retención; SQLite entero no se cifra aquí.

Ver TESTS.md, EVIDENCE.md, RISKS.md y DECISIONS.md de esta campaña. La presencia del código no aprueba una instalación Odoo no ejecutada.
