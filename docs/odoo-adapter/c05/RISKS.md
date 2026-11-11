# Riesgos C05

Ensayar restauración WAL y copia representativa anterior fuera de datos reales, medir concurrencia y disco.

No se ha ejecutado Odoo real en esta entrega. Mantener el feature flag desactivado en producción. Ante fuga de tenancy, pérdida de auditoría, firma omitida, duplicación, posible publicación o fiscalidad ambigua sin bloqueo, detener y resolver. Modelo transversal: [threat-model.md](../threat-model.md).
