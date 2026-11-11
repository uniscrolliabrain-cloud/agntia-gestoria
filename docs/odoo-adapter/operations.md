# Operaciones del adaptador

Esta entrega es una implementación para laboratorio, con validación Odoo real pendiente. No desplegar automáticamente en producción. Leer también RUNBOOK.md y pilot-acceptance.md.

## Entorno de servidor

Python >=3.11 (receta probada de sintaxis en 3.12), Node >=22.13. Instalar `python -m pip install -e .` desde root. Para desarrollo usar `.[dev]`. Se añaden httpx y cryptography; la base y UI anteriores permanecen. Activar explícitamente `ODOO_ADAPTER_ENABLED=true`; por defecto no crea tablas de integración ni ejecuta HTTP.

`ODOO_SERVERS_JSON` es un registro de administrador, no un campo del chat. Cada referencia necesita base_url HTTPS privada, database, api_key_env, gestoria_company_id, tenant_id, odoo_company_id, expected_instance_id y allowed_networks. Discovery exige el SHA Odoo fijado. write_enabled=false por defecto; además IDs autorizados de partner/journal/account/tax y tax_mappings explícitos para proyectar borradores. La clave API está en la variable referenciada; usar inyección de un gestor de secretos en producción.

Modo standalone usa tenant `standalone:<cid>` y autentica con el sistema existente; el owner local sin token solo se permite si además ODOO_ALLOW_LOCAL_OWNER=true. Modo integrado usa ámbitos por actor configurados en servidor. Nunca enviar las variables al frontend.

Credenciales separadas: API key bot por DB, HMAC approval_signing_key_env y ODOO_DOCUMENT_KEY Fernet. Odoo monta el mismo verificador HMAC desde fichero secreto; cambiar el firmante requiere actualizar ambos extremos coordinadamente. Rotar API key conservando api_key_env, revalidar y comprobar permisos; no borrar links ni historial. La clave de documentos no tiene keyring multiversión en este MVP: conservar la anterior para recuperar originales y planificar recifrado con backup, no sobrescribirla a ciegas.

El worker `agntia-gestoria-odoo-worker --data-dir RUTA` procesa jobs persistidos; `--once` ejecuta una iteración. La API no es un scheduler. Las capacidades expiran en una hora: un humano/servicio autorizado debe revalidar el binding y relanzar jobs bloqueados conforme a política, no cambiar automáticamente a owner.

## Datos, backup y rollback

Primera migración aditiva crea una copia SQLite en migration-backups antes de DDL. Transacciones BEGIN IMMEDIATE y WAL; backup operativo debe incluir DB consistente, ficheros cifrados, política y claves externas recuperables. La copia SQLite sola no contiene originales/documentos ni secretos. Probar recuperación antes de piloto. Odoo requiere PostgreSQL y filestore consistentes; el script de laboratorio los respalda deteniendo servicios nombrados.

Desactivar ODOO_ADAPTER_ENABLED y reiniciar API/worker detiene operaciones nuevas. No borrar tablas ni movimientos para revertir. Una escritura incierta se concilia por ledger, nunca por otro create. Tras desactivar pueden seguir descargándose originales locales mediante los permisos documentales existentes.

La API metrics mide últimas 10000 llamadas por conexión, p50/p95, fallos y conflictos; no mide infraestructura ni coste completo. Añadir monitorización externa de disco/WAL, lag, expiración de credenciales, backlog y backups antes de producción. Métricas sin TTL/retención automática pueden crecer: definir mantenimiento y archivo fuera de horas, preservando auditoría.

No guardar exports de staging, fixtures.private.json, run-env.json, logs privados ni secretos en GitHub/artefactos CI. Limitar accesos, cifrar disco/backups y revisar retención legal/RGPD según documento. Esta implementación cifra originales importados; no declara cifrado de todo SQLite.
