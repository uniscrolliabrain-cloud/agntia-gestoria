# Riesgos C19

Wiring AgntiaPro solo con aprobación; verificar gateway/event bus/policy/approval service y deduplicación del consumidor.

No se ha ejecutado Odoo real en esta entrega. Mantener el feature flag desactivado en producción. Ante fuga de tenancy, pérdida de auditoría, firma omitida, duplicación, posible publicación o fiscalidad ambigua sin bloqueo, detener y resolver. Modelo transversal: [threat-model.md](../threat-model.md).
