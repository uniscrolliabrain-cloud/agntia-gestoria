# ADR 0001 · Implementación por lote, pruebas reales pendientes

Fecha: 2026-11-09. Base remota: `1fd25d932a26acab0d865aa4aa3d7ed83876282e`.

El propietario ha indicado: «termina de implementar todas fases del módulo odoo de una vez y luego te corro test y te hago el docker de todo con la otra IA en autonomo». Esta instrucción autoriza implementar C03–C20 por lote sin detener la escritura de código en cada gate de Docker. No convierte los gates no ejecutados en PASS, no autoriza producción y no amplía el alcance a `agente`.

Se conserva el manifiesto original de 43 fuentes. `approved-source-changes.json` enumera los hashes antiguos/nuevos exactos de los archivos originales modificados por este lote. El verificador rechaza cualquier modificación adicional. Fórmulas, reglas territoriales, fuentes legales, storage original y flujo original de revisión no tienen exenciones.

Cambios mínimos de producción: app registra un router adicional y permite recuperar documentos importados cifrados mediante la autenticación documental existente; pyproject añade transporte, cifrado y CLI worker; Hono añade una allowlist exacta para las rutas Odoo; build/package publican módulos SDK aditivos. La CI ejecuta las nuevas pruebas. No se reescriben motores ni rutas previas.

El addon propio es necesario para snapshots coherentes, identidad de base comprobable, creación transaccional con ledger idempotente y verificación de aprobación humana firmada. Un `account.move/create` genérico no ofrece estas garantías frente a credenciales agénticas. Se divide bridge/base y extensión account para poder desactivar contabilidad si falta el módulo.

La aprobación HMAC se liga a instancia DB, compañía, operación, payload, aprobador y caducidad. La cuenta bot no puede publicar mediante métodos genéricos; sus escrituras en modelos protegidos exigen un marcador Python que JSON no puede fabricar. La efectividad real de ACL/ORM y locks se debe probar en Odoo 19.

Conflictos remotos generan un marcador económico cero no verificado para invalidar los fingerprints existentes sin modificar analytics/engines. Se conserva el original y se exige resolución humana. La decisión `supersede_local` anula localmente y archiva enlaces, nunca borra movimientos remotos.

Decisiones de despliegue: feature flag desactivada por defecto, un SQLite con WAL y transacciones BEGIN IMMEDIATE, worker explícito con leases; no scheduler empresarial paralelo. La futura integración Organizacional pertenece a AgntiaPro. Docker/piloto/backup real siguen NOT VERIFIED hasta ejecución externa.
