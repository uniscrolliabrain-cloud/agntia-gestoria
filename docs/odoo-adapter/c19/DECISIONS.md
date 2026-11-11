# Decisiones C19

Se implementa herramientas, eventos y rota sin reescribir la API original ni convertir el ERP en producto visible. La instrucción posterior del propietario autoriza avanzar el código en lote; los gates no ejecutados permanecen abiertos. Ver [ADR0001](../adr/0001-batch-implementation.md).

Consolidación deliberada: Service concentra registry/binding/policy; Imports concentra staging/cursor/conflictos; Commands concentra propuestas/aprobaciones/write-back; reads+mappers concentran lectura. No crear archivos vacíos con cada nombre propuesto como evidencia de funcionalidad.

Herramientas lectura/propuesta sin approve/commit, outbox/inbox/ACK y briefing basado en registros persistidos; contrato de rotas, sin scheduler paralelo.
