# Laboratorio C03 de Odoo Community

Este proyecto Compose usa exclusivamente datos sintéticos. Arranca Odoo y PostgreSQL sin publicar puertos en el host. La cuenta SQL de Odoo es dueña de las dos bases de laboratorio y carece de privilegios de administración del clúster. El proceso se valida en un runner Linux con Docker en el workflow **Odoo C03 lab**.

## Ejecutar

Se necesita Docker con Compose v2, un motor de contenedores Linux y Bash. En Windows, usar Git Bash con el CLI de Docker accesible.

1. En este directorio, copiar `.env.example` a `.env` y poner dos secretos distintos, aleatorios y exclusivos del laboratorio. No reutilizar credenciales de otra instalación. El volumen PostgreSQL conserva las credenciales con las que se inicializó.
2. Ejecutar `docker compose config --quiet` y `bash lab.sh up`. La base `agntia_test_a` instala base y contactos. La base `agntia_test_b` instala también contabilidad y localización española. El script comprueba estados reales en PostgreSQL e imprime las versiones de los módulos instalados.
3. Ejecutar `bash lab.sh smoke`. Crea un contacto y un usuario técnico de prueba por base, usa una clave JSON-2 efímera y comprueba lectura y rechazo de la misma clave en la otra base. El fixture se retira al terminar. Estas pruebas miden el alcance de la credencial por base; las reglas entre compañías y las restricciones del adaptador necesitan casos adicionales.
4. Ejecutar `bash lab.sh recovery` para detener Odoo, crear un backup de la base B y su filestore, registrar sus checksums, restaurar en una base temporal y comprobar que un adjunto restaurado conserva sus bytes. La base temporal y los archivos de prueba se eliminan al terminar. Si el ensayo falla y Odoo queda detenido, volver a arrancarlo con `bash lab.sh up` tras revisar el fallo.
5. Ejecutar `bash lab.sh stop` al terminar. Conserva los volúmenes. Si falla un arranque, revisar `bash lab.sh logs`. Una inicialización parcial se detecta por la comprobación de módulos; el script evita reinstalar automáticamente sobre una base existente.

Odoo usa el manifest amd64 de [UPSTREAM.md](UPSTREAM.md). PostgreSQL usa el índice OCI de `postgres:16-bookworm` consultado en el registro. La ejecución valida la combinación concreta; la equivalencia entre el código auditado y el paquete nightly de Odoo sigue pendiente.

## Alcance de la evidencia

El workflow registra el arranque, la matriz de módulos, una segunda ejecución del bootstrap, las consultas JSON-2 y el ensayo de restauración. Las comprobaciones se ejecutan en un proyecto dedicado `agntia-odoo-lab`. Los resultados y las comprobaciones pendientes se detallan en la [evidencia de C03](../../docs/odoo-adapter/c03/EVIDENCE.md).
