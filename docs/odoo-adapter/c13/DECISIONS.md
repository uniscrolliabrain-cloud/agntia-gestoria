# Decisiones C13

Se implementa sync incremental y reconciliación sin reescribir la API original ni convertir el ERP en producto visible. La instrucción posterior del propietario autoriza avanzar el código en lote; los gates no ejecutados permanecen abiertos. Ver [ADR0001](../adr/0001-batch-implementation.md).

Consolidación deliberada: Service concentra registry/binding/policy; Imports concentra staging/cursor/conflictos; Commands concentra propuestas/aprobaciones/write-back; reads+mappers concentran lectura. No crear archivos vacíos con cada nombre propuesto como evidencia de funcionalidad.

Cursor write_date con overlap, escaneo por id y watermark tras commit, missing en fullscan, leases/heartbeats/retries y dead-letter por estado bloqueado.
