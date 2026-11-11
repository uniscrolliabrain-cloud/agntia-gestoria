# Decisiones C15

Se implementa contactos write-back sin reescribir la API original ni convertir el ERP en producto visible. La instrucción posterior del propietario autoriza avanzar el código en lote; los gates no ejecutados permanecen abiertos. Ver [ADR0001](../adr/0001-batch-implementation.md).

Consolidación deliberada: Service concentra registry/binding/policy; Imports concentra staging/cursor/conflictos; Commands concentra propuestas/aprobaciones/write-back; reads+mappers concentran lectura. No crear archivos vacíos con cada nombre propuesto como evidencia de funcionalidad.

Dry-run inmutable, aprobación humana firmada ligada a DB, expected_write_date, ejecución única por propuesta y lectura de ledger tras incertidumbre.
