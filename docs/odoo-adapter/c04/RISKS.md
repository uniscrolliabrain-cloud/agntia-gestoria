# Riesgos C04

Ejecutar contratos de proveedor reales además de validación local; cotejar cliente/servidor con payloads capturados sin PII.

No se ha ejecutado Odoo real en esta entrega. Mantener el feature flag desactivado en producción. Ante fuga de tenancy, pérdida de auditoría, firma omitida, duplicación, posible publicación o fiscalidad ambigua sin bloqueo, detener y resolver. Modelo transversal: [threat-model.md](../threat-model.md).
