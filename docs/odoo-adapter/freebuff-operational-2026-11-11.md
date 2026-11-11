# Entrega operativa de Freebuff · 11 de noviembre de 2026

La rama freebuff/gestoria-autonomo incorpora las correcciones revisadas y la implementación heredada del adaptador. La PR #13 integra el conjunto en main. El propietario autorizó su validación e integración.

## Cambios aplicados

- El modo propietario local se activa mediante GESTORIA_ALLOW_LOCAL_OWNER=true. La configuración normal exige credenciales.
- El navegador recibe una sesión opaca con hash persistido, caducidad de ocho horas y revocación al cerrar sesión. Rotar el token invalida sus sesiones. El login limita intentos por cliente y el origen HTTPS público se configura mediante GESTORIA_PUBLIC_ORIGIN.
- El guardado comprueba ID, empresa y clase. Actualiza una clave única nueva y conserva la existente cuando el caller omite ese argumento.
- Las métricas registran sus fallos de SQLite y conservan el resultado o error original del proveedor. Hay sondas de vida y disponibilidad local de DB.
- El cierre de expedientes requiere owner o reviewer en API y UI. El catálogo de herramientas de agente omite esa operación.
- El error público incierto devuelve reconciliación y retryable=false. El SDK y sus declaraciones conservan category y next_action.
- Las operaciones persistidas llevan fecha de creación. Su relectura clasifica la ventana de revisión y conserva las claves, incluso después de la ventana, para recuperar el resultado sin repetir efectos.
- Odoo usa data_dir=/var/lib/odoo, el volumen que respalda el script de filestore. El workflow ejecuta el laboratorio sobre esta rama y conserva diagnósticos privados sanitizados.

## Evidencia

La ejecución real [43025348001](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/actions/runs/43025348001) pasó build, aprovisionamiento de dos bases, sonda HTTP, smoke, los seis casos reales, backup y restauración con lectura del adjunto mediante ORM.

La suite local de la primera corrección pasó 90 casos Python y cuatro Node. La regresión adicional de retención persistida verifica que una clave antigua devuelve el resultado previo y un solo efecto. Los checks de la PR identifican el resultado del commit candidato final.

## Correcciones a la auditoría histórica

Las cinco partes audit-2026-11-11*.md describen el corte original y deben interpretarse junto con esta actualización.

- El workflow compara base y head de un PR. La combinación original sí se ejecutó para la rama prevista. Se extendió el disparador a Freebuff y main.
- Las migraciones usan BEGIN IMMEDIATE y comprueban versión dentro del lock. Se probaron seis llamadas concurrentes. Los arranques posteriores a la migración no generaron nuevos backups. Puede haber copias redundantes durante el arranque concurrente.
- El acuse comprueba e inserta dentro de BEGIN IMMEDIATE, que serializa escritores. La carrera descrita en el informe requiere una reproducción adicional.
- El contexto de conexión confirma una sola vez la transacción. La validación remota y la transacción SQLite operan sobre sistemas independientes.
- El corte original tenía 47 códigos, 27 pruebas nuevas y 20 archivos de diferencia. Los valores menores del handoff corresponden a cortes anteriores.
- La revisión de licencias debe examinar avisos y obligaciones por componente antes de concluir incompatibilidad.

## Alcance de operación

La evidencia real usa datos sintéticos y el build fijado en el laboratorio. Incluye importación con revisión, frontera canaria sintética, separación de bases, detección de cambios y replay de borradores mediante ledger. La integración final del SDK en agente y el piloto con datos de empresas siguen sus campañas y contratos de identidad.
