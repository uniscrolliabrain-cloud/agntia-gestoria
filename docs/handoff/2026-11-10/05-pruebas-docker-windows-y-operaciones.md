# 05 · Pruebas, laboratorio Windows/Docker, evidencias y operación

Fecha de corte: 10 de noviembre de2026. Este documento es el relevo operativo para la IA del laptop del propietario. La decisión del usuario es ejecutar la demo en su PC, con sus herramientas ya disponibles, sin contratar alojamiento. Esta carpeta documenta la continuidad; no demuestra que los comandos Docker se hayan ejecutado ni amplía autorización a datos reales o producción.

## Evidencia que sí existe

La implementación principal del adaptador se publicó en `84504053d71c966db58d8de0fdf44b9817ebef82`. La CI registrada en `docs/odoo-adapter/c20/ci-results.json` ejecutó57 tests Python, todos aprobados, sin workaround del selector, y cuatro escenarios Node aprobados. El job comprobó instalación dev, build del SDK, baseline, sintaxis JS y navegador sobre el dashboard existente, incluyendo escritorio/móvil, descarga de informe y creación de registro.

La ejecución CI es https://github.com/uniscrolliabrain-cloud/agntia-gestoria/actions/runs/42720444812, job129512737755. Python tardó7.079 segundos en esa ejecución. Son medidas de esa revisión y runner, no un benchmark de Odoo ni un SLA. Las revisiones posteriores documentales pueden volver a ejecutar workflows, pero no inventar su resultado sin consultarlo.

Localmente se ejecutaron también57 tests con un ajuste temporal de selectors para resolver el comportamiento de TestClient en este sandbox. El ajuste limitaba la espera de select a20ms y solo se aplicó al proceso de prueba. No está en producción ni debe copiarse al laptop como requisito universal. La CI estándar aprobada confirma que el código no dependía de ese ajuste.

El runner Node local informó un archivo aprobado que declaraba cuatro escenarios; en CI sí hubo cuatro resultados individuales. Esta diferencia se registró expresamente. No sumar ambos como cinco tests o atribuir al sandbox cuatro resultados que no informó. La instalación editable runtime dentro de .venv y la ayuda del worker se comprobaron; un intento global falló por home de solo lectura y se resolvió usando el venv, sin cambiar permisos generales.

## Lo que no se ha probado todavía

No se ha arrancado aquí Odoo/PostgreSQL reales, instalado los addons propios, verificado su ACL/ORM ni ejecutado sus carreras de concurrencia. Tampoco consta backup/restore real de Odoo, contratos JSON-2 reales, rotación completa, recuperación de fallos externos o E2E fiscal con Hacienda. La suite live está preparada, no aprobada.

La suite de navegador valida el dashboard y recorridos actuales, no todas las futuras pantallas de ventas, bancos, laboral o AgntiaPro. Los tests simulados comprueban reglas importantes de autorización, importación, conflictos, firmas y replays, pero no garantizan compatibilidad de un addon con todos los caminos ORM de Odoo19.

La antigua auditoría C02 tuvo38 comprobaciones estáticas de fuente. No son38 tests de una instancia. C01 inventarió43 fuentes base. Esos números no deben mezclarse con57 tests Python. El snapshot agntia-gestoria.txt de la campaña no está acreditado como cotejado si no se proporcionó el archivo real correspondiente.

## Primeros pasos del laptop

El propietario puede clonar en la ruta Windows que prefiera; no conocemos esa ruta. `/workspace/Agntia-gestoria` es el checkout del implementador, no una ruta del PC del usuario. Antes de cambiar de rama comprobar git status y conservar cambios locales. No ejecutar reset hard o limpiar archivos del propietario para igualar un ejemplo.

Desde un clon limpio, la receta del handoff es:

```powershell
git fetch origin
git switch feat/odoo-complete-adapter
$Lab = Join-Path $env:LOCALAPPDATA 'AgntiaGestoriaSyntheticLab'
.\scripts\odoo_verify.ps1 -StateDir $Lab -Provision -StartApp
```

Requisitos de la receta: Docker Desktop con contenedores Linux/WSL2 o un daemon equivalente local, Composev2, Git, Python3.12 y Node24. Verificar el contexto Docker local antes de provisionar. Los scripts rechazan DOCKER_HOST heredado; aun así el operador debe asegurarse de que no seleccionó un daemon remoto accidentalmente.

Si PowerShell bloquea el script por política, el propietario decide su política o se ejecutan los comandos equivalentes del Runbook. La IA no debe cambiar una política global de ejecución sin autorización. No asumir que tener Docker instalado significa que el daemon y WSL están en ejecución.

## Qué provisiona el laboratorio

`infra/odoo/compose.yaml` define un proyecto sintético nombrado, PostgreSQL17 fijado por digest, Odoo con fuente exacta superpuesta, red interna y volúmenes persistentes. El perfil app añade API Gestoría y worker compartiendo datos locales. Los puertos publicados son loopback8069 para Odoo y8010 para Gestoría; PostgreSQL no publica puerto.

El Dockerfile de Odoo no confía en que la fuente de una imagen nightly coincida con el SHA auditado: obtiene el código exacto y configura su entorno. Discovery comprueba el marcador. La compatibilidad real del build y sus dependencias sigue siendo una de las primeras pruebas que hay que ejecutar.

El bootstrap prepara estado privado fuera del repo y genera secretos de prueba. Crea agntia_test_a y agntia_test_b, instala módulos mínimos y addons, y ejecuta fixtures sintéticos. Un caso usa autónomo de territorio común con IVA; el otro SL canaria con IGIC. Hay bots distintos por base y credenciales Gestoría de humanos/agentes para comprobar scopes.

Los ficheros run-env.json, fixtures.private.json, configuración privada, claves, dumps y logs privados no se suben a GitHub ni se pegan en el chat. El directorio debe protegerse con permisos del propietario, especialmente en NTFS. La carpeta tiene un marcador de laboratorio que los scripts exigen; el marcador no reemplaza comprobar que no se apunta a datos ajenos.

## Scripts disponibles y responsabilidades

`odoo_bootstrap.py` separa prepare, bootstrap y start-app. No sobreescribe silenciosamente un estado existente. El fixture rechaza recrear el bot si ya existe, para no rotar credenciales o duplicar documentos sin control. Si el primer bootstrap se corta a mitad, inspeccionar el estado antes de intentar continuar o destruirlo.

`odoo_smoke.py` comprueba bindings e importación con el proveedor real de laboratorio. `odoo_run_local.py` permite API o worker en host; `--once` sirve para una iteración de worker. `odoo_reconcile.py` consulta una operación incierta existente y no repite create. `odoo_reset_test.py` destruye exclusivamente el proyecto/volúmenes sintéticos con confirmación explícita; no se usa contra producción.

`odoo_backup.py` respalda PostgreSQL y filestore sintéticos deteniendo servicios nombrados para consistencia. La restauración tiene destino fijo agntia_test_restore y verifica identidad/checksums/conteos. El script no es una política completa de backup empresarial. SQLite, originales cifrados y claves de Gestoría necesitan su plan de recuperación también.

La ayuda y argumentos exactos viven en scripts y Runbook. No convertir un comando de destrucción en paso automático de una prueba que pueda ejecutar otro humano sin entender su efecto. Si el estado anterior tiene valor, respaldarlo y verificar recuperación antes de sustituirlo.

## Suites y escenarios reales pendientes

La suite normal usa unittest discover sobre tests. La suite live se ejecuta con discover en tests/integration, exige AGNTIA_RUN_ODOO_TESTS=1 y la ruta privada AGNTIA_LAB_STATE_DIR. Un skip no es un PASS de integración. Se mantiene opt-in para no usar accidentalmente un servidor existente.

Los escenarios A–E incluyen importación/documento/revisión/cálculo/reporte, bloqueo del motor común para Canarias, aislamiento entre dos bases, cambio remoto con invalidación y replay de borrador. El caso D usa un snapshot de cálculo sintético: ampliar a una revisión/cálculo completo después de cambio real antes de declararlo cobertura integral. E simula pérdida del ACK local tras transacción real; falta además provocar timeout de red y concurrencia remota.

Hay que ensayar instalación sin account, cuenta sin permisos, credenciales cruzadas, API key revocada, capacidades caducadas, módulo cambiado, fallo de SQLite, lease expirada, crash entre HTTP/ACK y restauración. Una doble solicitud simultánea debe producir un único borrador/ledger y ningún posted. No llamar action_post para probar una emisión que sigue fuera del alcance autorizado.

## Registro de resultados y operación posterior

Cada ejecución debe conservar SHA de aplicación/addons, digest de imagen construido, versiones, comandos, duración, conteo de tests y fallos/skips. Los logs publicados se redactan; los originales privados se conservan en el equipo autorizado. Si algo falla, reportar FAIL o BLOCKED con la causa y un siguiente paso, no alterar el test o aumentar permisos del bot para ocultar el problema.

Los fallos de ámbito, publicación posible, firma omitida, secreto, pérdida de auditoría o duplicado detienen el piloto hasta corregirlos. Las métricas existentes miden operaciones observadas; medir lag, backlog, disco, consumo y coste real antes de prometer capacidad. No hay un coste cloud real contratado en este chat.

El rollback inicial es desactivar la feature flag y reiniciar los servicios pertinentes, conservando tablas, evidencias y operaciones inciertas. Reconciliar movimientos existentes, nunca borrarlos para simular reversión. Para producción futura se necesitan aceptación del propietario, red privada/TLS, custodia de certificados, backups externos y recuperación probada. La demo del PC puede completarse sin adelantar ninguna de esas contrataciones.


## Fuentes internas para continuar

- [Evidencia CI registrada](../../odoo-adapter/c20/ci-results.json).
- [Runbook](../../odoo-adapter/RUNBOOK.md).
- [Script PowerShell](../../../scripts/odoo_verify.ps1).
- [Suite live pendiente](../../../tests/integration/test_odoo_live.py).
- [Compose sintético](../../../infra/odoo/compose.yaml).
- [Criterios de piloto](../../odoo-adapter/pilot-acceptance.md).

Siguiente lectura: [índice y protocolo de uso](README.md). La evidencia se atribuye al SHA/entorno descrito, no a cualquier checkout posterior.
