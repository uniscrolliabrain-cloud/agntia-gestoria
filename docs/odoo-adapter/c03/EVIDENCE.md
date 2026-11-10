# C03 · Evidencia de ejecución en Linux

Fecha: 10 de noviembre de 2026. Entorno: runner Linux efímero de GitHub Actions, datos sintéticos y proyecto Docker `agntia-odoo-lab`. Implementación y revisión en la [PR #7](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/pull/7).

| Caso | Resultado observado |
| --- | --- |
| C03-01. Validar Compose y arrancar las imágenes fijadas | PASS. El proceso informó `Odoo Server 19.0-20261102`. El healthcheck consultó también el estado del servidor PostgreSQL. |
| C03-02. Comprobar variantes de módulos | PASS. A: `base` 19.0.1.3 y `contacts` 19.0.1.0, sin `account` instalado. B: los mismos más `account` 19.0.1.5 y `l10n_es` 19.0.5.4. |
| C03-03. Repetir bootstrap | PASS. El segundo arranque reutilizó ambas bases y volvió a validar los módulos. |
| C03-04. Probar JSON-2 y alcance de las credenciales | PASS. Cada usuario sintético leyó su contacto por JSON-2. Se rechazó su clave al usarla contra la otra base y se denegó la lectura del modelo administrativo en su propia base. |
| C03-05. Restaurar datos y filestore | PASS. Backup con SHA-256, restauración en una base temporal, comprobación de módulos en la copia y recuperación de los bytes conocidos de un adjunto desde el archivo del filestore. Odoo volvió a arrancar tras el ensayo. |

Evidencia principal: [ejecución 42832723408](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/actions/runs/42832723408), commit `3a2e20554013a004c049a612afe4546635644127`. Ejecuciones precedentes: [primer arranque y JSON-2](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/actions/runs/42832349606) y [primer ensayo de restauración](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/actions/runs/42832557290).

## Límites y verificaciones pendientes

- C02 conserva por separado el código Community auditado y la imagen nightly. El éxito del runner acredita la imagen concreta. Su equivalencia exacta con el SHA de código sigue **NOT VERIFIED**.
- Los resultados de C03 corresponden al aislamiento de credenciales entre bases y al modelo administrativo probado. Falta probar contactos compartidos y compañías hermanas bajo el binding de Gestoría. El laboratorio todavía carece de pruebas JSON-2 de lectura de facturas y del comportamiento de los modelos contables para un bot con permisos contables mínimos.
- La restauración recuperó SQL y un archivo con contenido conocido en ubicaciones temporales. Queda pendiente arrancar un Odoo independiente contra la base restaurada y leer el adjunto por el ORM.
- El entorno no contiene el adaptador de Gestoría ni el runtime de Agente. El ensayo de integración entre ambos repositorios sigue pendiente.
