# Riesgos C17

Instalación ORM/ACL real, dos solicitudes simultáneas y comportamiento de aislamiento/retry PostgreSQL. No afirmar que está instalado.

No se ha ejecutado Odoo real en esta entrega. Mantener el feature flag desactivado en producción. Ante fuga de tenancy, pérdida de auditoría, firma omitida, duplicación, posible publicación o fiscalidad ambigua sin bloqueo, detener y resolver. Modelo transversal: [threat-model.md](../threat-model.md).
