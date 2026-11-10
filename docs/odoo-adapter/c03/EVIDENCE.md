# C03 · Evidencia de ejecución en Linux

Fecha: 10 de noviembre de 2026. Entorno: runner Linux efímero de GitHub Actions, datos sintéticos y proyecto Docker `agntia-odoo-lab`. Implementación y revisión en la [PR #7](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/pull/7).

| Caso | Resultado observado |
| --- | --- |
| C03-01. Validar Compose y arrancar las imágenes fijadas | PASS. El proceso informó `Odoo Server 19.0-20261102`. El healthcheck consultó también el estado del servidor PostgreSQL. |
| C03-02. Comprobar variantes de módulos | PASS. A: `base` 19.0.1.3 y `contacts` 19.0.1.0, sin `account` instalado. B: los mismos más `account` 19.0.1.5 y `l10n_es` 19.0.5.4. |
| C03-03. Repetir bootstrap | PASS. El segundo arranque reutilizó ambas bases y volvió a validar los módulos. |
| C03-04. Probar JSON-2 y alcance de las credenciales | PASS. Cada usuario sintético leyó su contacto por JSON-2. Se rechazó su clave al usarla contra la otra base y se denegó la lectura del modelo administrativo en su propia base. |
| C03-05. Restaurar datos y filestore | PASS. Backup con SHA-256, restauración en una base temporal y lectura de los bytes conocidos del adjunto por el ORM de un proceso Odoo separado. El ORM usó un directorio de datos temporal con el filestore restaurado. Odoo volvió a arrancar tras el ensayo. |
| C03-06. Probar dos compañías en una misma base | PASS. El bot leyó el contacto propio y el compartido, no obtuvo el contacto de la otra compañía y recibió 403 al forzar su contexto. La visibilidad nativa de compartidos obliga a filtrar explícitamente en Gestoría. |
| C03-07. Lectura contable por rol y variante | PASS. Sin `account`, `account.move` devolvió 404. En B, el bot interno recibió 403 y el bot con `account.group_account_readonly` leyó el borrador. Se verificaron campos de movimiento, línea, impuesto y cuenta, además de la lectura de compañía, diario y moneda. |
| C02-RT. Comparar archivos instalados y auditados | 15 archivos comparados, 9 iguales, 6 diferentes y 0 ausentes. Diferencias en `release.py` y los modelos de contacto, movimiento, línea, impuesto y cuenta. Las pruebas de runtime se atribuyen a la imagen instalada. |

Evidencia principal: [ejecución 42887714922](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/actions/runs/42887714922), commit `b182a78ee8b7ad819a72747905d4c2391872c1b6`. Ejecuciones precedentes: [primer arranque y JSON-2](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/actions/runs/42832349606) y [primer ensayo de restauración](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/actions/runs/42832557290).

## Límites y verificaciones pendientes

- C02 conserva por separado el código Community auditado y la imagen nightly. El subconjunto comparado contiene diferencias de bytes. La cobertura de contrato corresponde únicamente a los casos registrados.
- La lectura contable se limitó a un borrador sintético sin líneas. Quedan pendientes los casos monetarios y fiscales de C11, las comprobaciones de autorización del binding propio de Gestoría y las pruebas con fixtures de compañías padre e hija.
- La recuperación acreditó la lectura con el ORM desde un proceso separado. La exposición HTTP de una instancia de recuperación queda fuera de esta prueba.
- El entorno no contiene el adaptador de Gestoría ni el runtime de Agente. El ensayo de integración entre ambos repositorios sigue pendiente.
