# C05 · Persistencia aditiva de la integración

Estado: primer corte de C05 para revisión, sobre los contratos de la PR #8. La migración es explícita y todavía no forma parte del arranque del servicio.

- `backup(database, destination)` utiliza el backup online de SQLite, verifica integridad y publica la copia completa sin sobrescribir archivos. El destino debe estar en un directorio existente cuyo sistema de archivos soporte enlaces duros. Es una copia de SQLite. El directorio de documentos requiere su respaldo aparte.
- `migrate(database)` reutiliza la transacción `BEGIN IMMEDIATE` de Gestoría. Aplica DDL por sentencia y registra el checksum de cada versión en la misma transacción. Repetir la migración es seguro. Si el historial diverge, la migración falla antes de aplicar más cambios.
- La empresa Gestoría pertenece a un tenant y las referencias de conexión, cursor y operación se relacionan mediante claves compuestas. Una pareja de referencias de endpoint y base con la misma compañía remota tiene una sola conexión. C06/C09 deben validar que dos referencias distintas no sean aliases del mismo destino.
- Las operaciones de contacto tienen clave idempotente única por conexión y un estado persistible de reconciliación. Un resultado confirmado exige ID remoto. La comprobación de aprobaciones, la comparación de payloads, las transiciones de ejecución y la reconciliación corresponden a sus servicios.

Quedan pendientes los vínculos con objetos locales, las colas de importación, el avance del cursor ligado al commit de un lote y la persistencia de aprobaciones. Los permisos del servicio y los secretos deben resolverse en C06. No se cambia `storage.py` ni se modifica la base de datos por iniciar Gestoría con esta rama.

## Pruebas

`python -m unittest discover -s tests -p test_odoo_migrations.py -v`

Los casos cubren backup de una base WAL previa con registros y auditoría, repetición de migración, rollback de DDL tras error, rechazo de checksum alterado, ejecución concurrente, cruce de tenant y restricciones de idempotencia.
