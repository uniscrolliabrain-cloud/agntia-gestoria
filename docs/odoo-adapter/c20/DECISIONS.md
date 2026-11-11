# Decisiones C20

Se implementa hardening y entrega sin reescribir la API original ni convertir el ERP en producto visible. La instrucción posterior del propietario autoriza avanzar el código en lote; los gates no ejecutados permanecen abiertos. Ver [ADR0001](../adr/0001-batch-implementation.md).

Consolidación deliberada: Service concentra registry/binding/policy; Imports concentra staging/cursor/conflictos; Commands concentra propuestas/aprobaciones/write-back; reads+mappers concentran lectura. No crear archivos vacíos con cada nombre propuesto como evidencia de funcionalidad.

Suite local, live A–E opt-in, backup/recovery scripts, CI normal y manual, runbooks y checklist de piloto.
