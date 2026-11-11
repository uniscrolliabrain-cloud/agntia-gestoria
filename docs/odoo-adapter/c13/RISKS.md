# Riesgos C13

Crash real fetch/commit/ack, modificación concurrente, avance de cursores sin pérdidas y re-sync completo.

No se ha ejecutado Odoo real en esta entrega. Mantener el feature flag desactivado en producción. Ante fuga de tenancy, pérdida de auditoría, firma omitida, duplicación, posible publicación o fiscalidad ambigua sin bloqueo, detener y resolver. Modelo transversal: [threat-model.md](../threat-model.md).
