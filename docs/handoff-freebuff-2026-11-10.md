# Handoff Freebuff · Gestoría, Odoo Community y Agente

Fecha de entrega: 10 de noviembre de 2026. Revisión prevista: 11 de noviembre de 2026, hora de Madrid. Este documento es el encargo para el agente autónomo y la guía para revisar su entrega. El objetivo inmediato es llevar el adaptador existente a una simulación reproducible con el runtime de Agente. Los 82 puntos forman un backlog priorizado, con entregas independientes que pueden revisarse mañana aunque queden olas pendientes.

## Punto de partida y ramas

- [PR #4](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/pull/4) contiene el adaptador de referencia, bridge, worker, SDK y laboratorio. Lee primero [su handoff](../ODOO-IMPLEMENTATION-HANDOFF.md), [el runbook](odoo-adapter/RUNBOOK.md) y [la aceptación del piloto](odoo-adapter/pilot-acceptance.md). La numeración de este documento identifica tareas de ejecución. C01–C20 sigue identificando las fases de la campaña.
- [PR #11](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/pull/11), rama `verify/odoo-complete-adapter`, es la base técnica. En el corte `b34b8ca2d33e4c87976b518c7816b063a4917a58` se renombró el argumento del bridge a `invoice_ids` porque JSON-2 reserva `ids`. Antes de tocar código, lee el resultado del [run lanzado para ese commit](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/actions/runs/42904254831). Antes de ese cambio pasaron el build, las dos bases y la sonda HTTP. El smoke falló al pedir snapshots de facturas. Comprueba si el nuevo run llegó más lejos.
- [PR #12](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/pull/12) contiene el cierre de expedientes reservado a personas y un harness reproducible en `scripts/simulation/`. Su ensayo recorrió clases reales de Agente, SDK, Hono y FastAPI con política inyectada y Odoo apagado. Reprodujo dos efectos simulados tras perder el ACK de la primera ejecución. Es el caso de regresión para la futura escritura. La PR está separada de la #11. Si una prueba necesita ambas, usa un commit de integración trazable en una rama desechable y anota ambos SHAs.
- [PR #7](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/pull/7) aporta evidencia del laboratorio independiente, incluidos módulos con y sin contabilidad, aislamiento de credenciales y recuperación por ORM. Sus resultados acreditan ese laboratorio, con una imagen nightly distinta del build desde código de la #11. Las PR #8–#10 están en pausa por solapamiento con la #4.
- El checkout de Agente usado en el ensayo estaba en `b37b67d4e18987402d255d377343a3454d723e5e`. Para reproducir el corte original usa ese SHA. Si ensayas otro commit, registra cuál y vuelve a medir la línea base.

## Preparación del worktree

Desde un clon limpio de `agntia-gestoria`, ejecuta los siguientes comandos. Si la ruta o la rama ya existe, inspecciónala y reutilízala si corresponde a este encargo. Antes de trabajar, verifica el resultado de `git status -sb` y `git log -1 --oneline`.

```powershell
git fetch origin refs/heads/docs/handoff-freebuff:refs/remotes/origin/docs/handoff-freebuff
git worktree add -b freebuff/gestoria-autonomo ../agntia-gestoria-freebuff origin/docs/handoff-freebuff
Set-Location ../agntia-gestoria-freebuff
git status -sb
git log -1 --oneline
```

La rama de documentación desciende del corte de la PR #11 indicado arriba. Compara con la rama remota de la #11 antes de empezar. Si ha avanzado, revisa el delta y documenta cómo incorporas los cambios. Usa `freebuff/gestoria-autonomo` para las primeras entregas y ramas `freebuff/<ola>-<tema>` para cambios grandes que necesiten revisión independiente. Abre PRs borrador contra la rama de la que realmente dependen. Deja commits pequeños y separa correcciones, pruebas y evidencia cuando facilite revisar el diff.

Trabaja con datos sintéticos y credenciales efímeras fuera del repo. Para el ensayo de Agente usa un checkout o worktree desechable. Mantén la instalación definitiva del SDK, los merges, el despliegue y los cambios de producción fuera de esta ejecución. Las decisiones humanas de una prueba deben quedar marcadas como sintéticas. Conserva el inventario congelado y presenta cualquier cambio protegido con hashes, ADR y regresión. Una fuga entre tenants, un bypass de aprobación, un secreto expuesto, un duplicado remoto o un resultado fiscal incorrecto detienen la ola afectada.

## Orden de trabajo y evidencia

1. Empieza por **01–10**. Diagnostica el primer fallo real, añade la regresión mínima, vuelve a ejecutar y deja el siguiente punto reproducible.
2. Continúa con **11–28**. Una lectura verde permite preparar la simulación de lectura. Las escrituras necesitan además las pruebas de revisión, aprobación, concurrencia y reconciliación.
3. Ejecuta **29–39**. Presenta la simulación desechable, sus limitaciones y una propuesta concreta de incorporación.
4. Prioriza **40–71** según los fallos y el alcance del piloto. **72–82** son proyectos posteriores. Documenta dependencias y alcance antes de abrir una implementación grande.

En cada entrega deja una entrada con ID de tarea, rama y SHA, dependencias, comandos, caso esperado y observado, enlace a ejecución, limitación y siguiente paso. Usa **PASS**, **FAIL**, **BLOCKED** o **NOT VERIFIED**. Un resultado con dobles y uno con Odoo real llevan registros separados. Para el relevo, agrupa las PRs en orden, indica cuáles están listas para revisión y enumera cualquier decisión pendiente.

## P0 · Laboratorio y pruebas reales

### 01 · Confirmar `invoice_ids`
Ejecuta el caso por JSON-2 y revisa las dos rutas del consumidor, paginación de snapshots y relectura antes del commit local. Añade una regresión que compruebe el nombre del argumento en la petición. **Salida:** ambos recorridos reciben el snapshot correcto y se registra el run que cubre el error anterior.

### 02 · Completar el smoke en A y B
Arranca las bases desde volúmenes nuevos y valida marcador, usuario técnico, compañía, capacidades y versiones. Previsualiza e importa el borrador sintético de cada una. **Salida:** dos resultados independientes con conteos, procedencia, estado local `unverified` y auditoría íntegra.

### 03 · Ejecutar la suite A–E
Usa el workflow de la PR #11 y el opt-in de laboratorio. Registra importación y revisión, variante canaria sintética, cruce de bases, cambio remoto y resultado incierto. Anota cualquier caso que use un snapshot preparado o un fallo simulado. **Salida:** matriz individual por caso, con fallos, saltos y límites visibles.

### 04 · Rechazar escrituras ORM genéricas
Usa un registro sintético y una modificación inocua para comprobar que el bot no puede escribir fuera del método cerrado del bridge. Relee el registro después. **Salida:** la operación se rechaza y el snapshot conserva los valores anteriores.

### 05 · Restaurar el adaptador completo
Haz backup de PostgreSQL y filestore en el laboratorio completo. Verifica hashes, restaura a una base nueva y lee por ORM el adjunto esperado. Reinicia la instancia original y comprueba su salud. **Salida:** evidencia de checksum, identidad del destino y coincidencia de bytes.

### 06 · Ejecutar el bridge sin contabilidad
Crea una variante con `base`, `contacts` y bridge base, sin el addon contable. Comprueba la lectura de contactos y consulta el informe de capacidades. **Salida:** contactos disponibles y facturas declaradas no disponibles, con respuesta estable en API y SDK.

### 07 · Probar caducidad y revocación
Emite una credencial sintética, verifica una lectura y repite tras revocarla. Prueba también una credencial caducada y contrasta con una caída de red. **Salida:** clasificación distinta de permisos y conectividad, sin exponer la clave ni elevar privilegios.

### 08 · Acreditar la procedencia del build
Registra SHA de código, imagen base, versión de Odoo, versión de PostgreSQL, módulos y marcador de bridge. Contrasta estos valores con el lock y con discovery. **Salida:** otra ejecución puede identificar exactamente el artefacto probado.

### 09 · Repetir el aprovisionamiento
Arranca desde cero, interrumpe una instalación sintética en un punto controlado y practica el procedimiento de recuperación. Documenta cuándo reutilizar el estado y cuándo crear uno nuevo. **Salida:** arranque limpio reproducible y recuperación sin sobrescribir un estado ajeno.

### 10 · Actualizar el informe de campaña
Vincula los casos observados a C02–C20. Distingue código escrito, unit tests, pruebas reales y piloto. **Salida:** cada avance tiene SHA y evidencia. Los requisitos pendientes tienen condición concreta para cerrarse.

## P0 · Aislamiento, permisos y revisión

### 11 · Validar cierre humano
Porta o integra la corrección de la PR #12 en una rama de ensayo. Repite API directa, Hono, SDK e interfaz con un expediente ya revisado. **Salida:** `owner` y `reviewer` pueden cerrar según política, `agent` y `viewer` quedan excluidos, y el catálogo del agente omite el cierre.

### 12 · Completar la matriz por rol
Enumera rutas y herramientas y cruza cada una con roles, revisión y alcance por empresa. Prioriza anulación, exportación, adjuntos, aprobación, commit y reconciliación. **Salida:** una tabla respaldada por pruebas positivas y negativas, incluida la API directa.

### 13 · Aislar compañías hermanas
En una misma base crea dos compañías hermanas y registros distinguibles. Configura un binding autorizado y recorre API y SDK con los dos actores. **Salida:** cada actor recibe únicamente su conjunto permitido y la prueba informa si Odoo y Gestoría aplicaron filtros distintos.

### 14 · Resolver contactos compartidos
Incluye un contacto con `company_id` vacío y demuestra primero el comportamiento nativo. Implementa o prueba la regla explícita elegida por Gestoría. **Salida:** el resultado coincide con esa regla y conserva procedencia cuando se admite una excepción autorizada.

### 15 · Aislar jerarquías de compañías
Repite el caso con compañía padre, hija y hermana. Comprueba el efecto de las reglas nativas y el filtro exacto del binding. **Salida:** la jerarquía no amplía el ámbito de Gestoría sin una autorización explícita.

### 16 · Cruzar identificadores de alcance
Construye una matriz que cambie solo uno de tenant, empresa local, conexión, DB, compañía remota y clave. Instrumenta si llegó a haber HTTP. **Salida:** cada combinación inválida se bloquea en la frontera adecuada y la respuesta omite metadatos ajenos.

### 17 · Rotar con trabajo en cola
Encola una tarea, cambia la revisión de conexión y arranca el worker. Repite con desactivación y revocación. **Salida:** el worker revalida alcance, estado y credencial antes de operar y deja el estado de la tarea explicable.

### 18 · Invalidar aprobaciones obsoletas
Cambia el contenido, revisión, empresa o conexión tras aprobar una propuesta sintética. Repite con caducidad. **Salida:** los cambios invalidan la aprobación anterior y el proveedor conserva su estado.

### 19 · Verificar la aprobación firmada
Prueba la firma válida y el intercambio de payload, operación, aprobador e instancia. Comprueba que los intentos fallidos dejan evidencia sanitizada. **Salida:** se ejecuta exclusivamente la combinación aprobada y permanece un solo resultado.

### 20 · Buscar fugas con centinelas
Inyecta valores sintéticos únicos como credenciales y comprueba logs, DTOs, errores, exportaciones y artefactos de CI. **Salida:** pruebas automáticas de ausencia en salidas públicas y una traza correlacionable sin secretos.

## P0 · Escrituras y recuperación de incertidumbre

### 21 · Timeout antes del commit
Inyecta una interrupción antes de que el bridge confirme el efecto y consulta el ledger con la misma clave. **Salida:** el sistema diferencia ausencia comprobada de resultado desconocido y solo permite continuar según esa evidencia.

### 22 · Timeout después del commit
Aplica el cambio sintético y pierde únicamente el ACK. Reconcilia por la misma clave y comprueba el objeto en Odoo. **Salida:** un efecto, un resultado reconciliado y ningún segundo create.

### 23 · Concurrentes con la misma clave
Coordina dos solicitudes para que coincidan en el mismo punto de ejecución. Prueba el resultado final en el bridge y en Gestoría. **Salida:** un objeto remoto y resultados compatibles o una espera explícita seguida del mismo resultado.

### 24 · Misma clave con otro contenido
Repite una operación confirmada modificando un campo relevante. **Salida:** conflicto estable, evidencia del hash anterior y conservación del resultado original.

### 25 · Reinicio entre commit y registro local
Detén el worker después de aplicar el efecto remoto y antes de confirmar el estado local. Reinicia con los mismos datos persistidos. **Salida:** se reanuda en reconciliación y no se duplica el efecto.

### 26 · Ledger remoto sin coincidencia
Compara respuesta autorizada de ausencia, timeout del ledger y error de permisos. **Salida:** únicamente la ausencia comprobada se representa como tal y los demás casos conservan el estado incierto.

### 27 · Retención del ledger
Calcula la ventana que deben cubrir reintentos, trabajos retrasados y restauraciones de backups. Prueba los límites y documenta el tratamiento de claves antiguas. **Salida:** política reproducible que evita reactivar una operación aún reconciliable.

### 28 · Contener el riesgo en el runtime
Ejecuta el harness de la PR #12 y reproduce el claim marcado como `failed` tras perder un ACK. Define qué capa traduce la incertidumbre y dónde queda persistida. **Salida:** antes de habilitar escrituras de Agente, la misma prueba debe conservar `outcome_unknown` y registrar un solo efecto. Mantén los commits aprobados en Gestoría mientras falte esta evidencia.

## P1 · Simulación e incorporación

### 29 · Probar el SDK empaquetado
Construye el SDK, genera un tarball y consúmelo en un proyecto temporal con la versión de Node y Hono del host. Comprueba imports, tipos y exports. **Salida:** el tarball probado queda identificado por versión y hash.

### 30 · Leer de extremo a extremo
Inyecta en el runtime desechable una capacidad de lectura que llegue a Gestoría y Odoo real. Elige un contacto o una factura sintética conocida. **Salida:** la lectura devuelve el dato normalizado esperado y una correlación permite seguir toda la cadena.

### 31 · Usar identidad del host
Sustituye el doble de política del primer ensayo por una sesión autenticada y una pertenencia sintética real. Resuelve token y binding del lado servidor. **Salida:** la entrada de la herramienta no puede elegir actor, tenant ni empresa.

### 32 · Ejecutar dos tenants en paralelo
Prepara sesiones y clientes SDK distintos. Intercala peticiones y revisa datos, cachés y trazas. **Salida:** cada respuesta y traza queda en su ámbito, incluso bajo concurrencia.

### 33 · Denegar una herramienta fuera de catálogo
Intenta ejecutar una capacidad no registrada y otra registrada para un rol distinto. **Salida:** el runtime las deniega antes del executor y el servicio no recibe una petición.

### 34 · Simular Gestoría caída
Detén el servicio sintético entre dos lecturas. Observa el estado del runtime, el mensaje al usuario y la recuperación. **Salida:** la lectura falla de forma acotada y puede recuperarse sin confundir el fallo con una respuesta vacía.

### 35 · Simular solo Odoo caído
Deja Gestoría disponible y corta el acceso a Odoo. Consulta datos locales y salud de la integración. **Salida:** se distinguen disponibilidad del servicio, frescura de datos y fallo remoto.

### 36 · Limitar lecturas lentas o incompletas
Inyecta latencia y una respuesta truncada. Mide timeout y verifica límites de respuesta, sanitización y presupuesto de reintentos. **Salida:** error tipado y tiempo acotado, con un resultado entendible para el consumidor.

### 37 · Completar el circuito humano
El agente prepara una propuesta, un actor humano sintético la aprueba y Gestoría ejecuta una operación autorizada. **Salida:** trazas de actor, revisión, hash, clave y efecto, con pruebas de denegación para el agente.

### 38 · Simular ACK perdido con Odoo real
Repite la pérdida posterior al commit con el bridge real y un runtime desechable. Correlaciona claim, registro local y ledger remoto. **Salida:** resultado incierto recuperado con la misma clave y un solo objeto.

### 39 · Preparar la incorporación mínima
Deja una propuesta revisable con versión fijada, identidad de servidor, catálogo de lectura y flag por tenant apagado. Adjunta la matriz de aceptación. **Salida:** PR candidata únicamente tras superar las pruebas aplicables y con procedimiento de desactivación.

## P1 · Importación y calidad de datos

### 40 · Probar paginación a escala
Genera más de mil contactos con nombres repetidos, Unicode, archivados y compañías distintas. Repite la paginación y compara IDs con el conjunto esperado. **Salida:** ninguna pérdida, duplicación o fuga.

### 41 · Cubrir empates de fecha
Fuerza el mismo `write_date` para más objetos que el tamaño de página. Usa fecha e ID como cursor y prueba el punto de corte. **Salida:** orden estable y reanudación completa.

### 42 · Cambiar datos entre preview e importación
Modifica un registro remoto tras previsualizarlo. Prueba la relectura del hash en la importación. **Salida:** el registro anterior no se confirma como vigente y aparece un conflicto con evidencia.

### 43 · Confirmar cursor y lote juntos
Provoca un fallo a mitad del guardado y otro justo después del commit. Reinicia y procesa la página otra vez. **Salida:** cursor, datos, enlaces y auditoría avanzan coherentemente.

### 44 · Distinguir archivado, borrado y acceso perdido
Prepara cada situación y compara la evidencia disponible. **Salida:** estados diferenciados y revisión cuando haga falta, conservando el historial local.

### 45 · Identificar objetos sin deduplicación especulativa
Prueba contactos con igual nombre o NIF y con IDs distintos. Usa conexión, modelo e ID técnico como referencia. **Salida:** los candidatos ambiguos se presentan a revisión y el replay exacto es idempotente.

### 46 · Ampliar la matriz de facturas
Añade fixtures de rectificativas, descuentos, varias líneas, impuestos incluidos y compuestos, y moneda distinta. **Salida:** cada fixture se mapea con evidencia o queda bloqueado con causa explícita.

### 47 · Separar líneas económicas y técnicas
Combina productos, notas, secciones, vencimientos y redondeos. Examina qué líneas influyen en importes y cuáles son informativas. **Salida:** el conjunto importado conserva el significado contable del fixture y registra exclusiones.

### 48 · Conciliar importes
Compara base, impuestos y total por moneda con valores esperados y prueba diferencias de redondeo. **Salida:** las discrepancias se explican o quedan en revisión, con precisión decimal conservada.

### 49 · Preservar revisiones ante cambios
Revisa un registro, modifica su origen y ejecuta sync. **Salida:** se conserva la revisión, se abre un conflicto y se señala la preparación afectada como obsoleta.

### 50 · Dar herramientas al operador
Diseña una vista que muestre el dato previo, el actual, su procedencia y decisiones disponibles según el rol. **Salida:** una persona puede resolver un caso sintético con auditoría del antes y después.

### 51 · Gestionar lotes parcialmente inválidos
Mezcla objetos válidos y errores de mapeo, permisos y datos. Define atomicidad o staging por caso y prueba reanudación. **Salida:** el informe explica qué quedó confirmado, bloqueado o pendiente.

### 52 · Probar adjuntos cifrados
Prueba tamaño, tipo, hash, integridad, empresa ajena y restauración. Ensaya rotación con copias sintéticas. **Salida:** se recupera el adjunto autorizado con el hash esperado y el actor ajeno queda bloqueado.

## P1 · Contratos, eventos y experiencia

### 53 · Inventariar eventos existentes
Revisa lectura y acuse del SDK de la PR #4. Contrasta con las necesidades del consumidor y el feed propuesto. **Salida:** decisión documentada sobre reutilizar, extender o versionar el contrato.

### 54 · Fijar el consumo del feed
Define orden, checkpoint, deduplicación, retención y recuperación de cursor expirado. Prueba reentrega y dos empresas. **Salida:** el consumidor confirma el cursor tras aplicar la página y nunca mezcla eventos.

### 55 · Publicar DTOs versionados
Exporta esquemas para operaciones realmente consumidas y valida ejemplos Python y TypeScript. Cubre importes, campos desconocidos y compatibilidad. **Salida:** el paquete y la API pasan la misma matriz de contratos.

### 56 · Normalizar errores
Crea casos de autenticación, permisos, ausencia, conflicto, caída y resultado incierto. Verifica la correspondencia API → SDK → runtime. **Salida:** errores estables, sanitizados y con acciones siguientes diferenciadas.

### 57 · Exponer frescura y procedencia
Define qué timestamps provienen del origen y cuáles de la observación local. Prueba estados reciente, obsoleto y desconocido. **Salida:** la UI puede explicar qué dato tiene y cuándo se verificó.

### 58 · Construir una primera vista
Elige registros o expedientes. Usa el modelo de lectura, valida accesos y prueba estados cargando, vacío, obsoleto y sin permisos. **Salida:** una vista útil respaldada por datos reales del ensayo.

### 59 · Definir cuándo Laia muestra una vista
Prueba conversaciones con y sin un cambio relevante, intención clara y permisos. **Salida:** decisiones reproducibles para vista, respuesta textual o solicitud de información.

### 60 · Enlazar afirmaciones a evidencia
Asocia cada cifra o estado relevante a un registro o documento autorizado. Prueba navegación con un actor de otra empresa. **Salida:** cada dato relevante es trazable y sus enlaces respetan alcance.

### 61 · Explicar obsolescencia
Crea una preparación y cambia el dato que la sustentaba. Muestra la modificación concreta y el siguiente paso de revisión. **Salida:** el usuario distingue el snapshot histórico de la situación actual.

### 62 · Mantener la fiscalidad en Gestoría
Revisa el consumidor para localizar cálculos o interpretaciones repetidas. Sustitúyelos por DTOs y capacidades de Gestoría cuando corresponda. **Salida:** ambos consumidores obtienen la misma decisión fiscal de una fuente común.

## P1 · Operación, recuperación y piloto

### 63 · Medir con cargas distintas
Ejecuta volúmenes pequeños, medios y grandes con datos sintéticos. Separa lectura, preview, importación y cola. **Salida:** p50, p95, errores y tamaño de muestra reproducibles.

### 64 · Instrumentar cada capacidad
Etiqueta duración y resultado por capacidad y categoría de fallo. Revisa cardinalidad y privacidad de las etiquetas. **Salida:** un operador puede diferenciar permisos, red, mapeo y validación sin datos sensibles.

### 65 · Alertar de degradación operativa
Inyecta sync atrasada, cola estancada, credencial revocada y resultado incierto. **Salida:** alertas diferenciadas con responsable, umbral y procedimiento de actuación.

### 66 · Probar concurrencia y WAL
Arranca API y worker contra una copia sintética. Prueba migración fallida, bloqueos y reintentos con dos procesos. **Salida:** historial y auditoría intactos, con comportamiento documentado ante contención.

### 67 · Restaurar el conjunto completo
Coordina SQLite, documentos cifrados, PostgreSQL, filestore y referencias a secretos. Recupera en un entorno separado y verifica enlaces. **Salida:** una lectura de extremo a extremo tras el restore y tiempos de recuperación medidos.

### 68 · Revertir por tenant
Activa una capacidad en un tenant de prueba y desactívala con operaciones pendientes. **Salida:** se detienen nuevas ejecuciones y sigue disponible la reconciliación autorizada.

### 69 · Preparar el runbook de incidentes
Escribe procedimientos de diagnóstico para revocación, binding equivocado, duplicado y resultado incierto. Valídalos mediante simulacros. **Salida:** otra persona puede ejecutar el procedimiento con evidencia y sin adivinar.

### 70 · Preparar un piloto de lectura
Selecciona un alcance acotado, responsables, métricas y condición de salida. Practica antes con un tenant sintético. **Salida:** checklist de aceptación y reversión listo para revisión del propietario.

### 71 · Preparar el primer contacto aprobado
Selecciona una sola operación y prueba aprobación, concurrencia, timeout y reconciliación. **Salida:** criterio de un efecto demostrado. Los borradores de factura conservan un gate independiente.

## P2 · Evolución del producto

### 72 · Diseñar compras y proveedores
Inventaría tareas de usuario y datos disponibles. Define primero lectura de proveedor, pedido o evidencia, y delimita cualquier propuesta de escritura. **Salida:** contrato de una vista inicial y un flujo de prueba.

### 73 · Mejorar la entrada de justificantes
Prueba carga, extracción, duplicados y documentos ambiguos. Distingue dato extraído de dato confirmado. **Salida:** la persona revisora puede corregir y conservar el documento y su procedencia.

### 74 · Construir una bandeja de revisión
Ordena expedientes por evidencia faltante, conflictos, antigüedad y siguiente acción. Verifica permisos y cambios concurrentes. **Salida:** la bandeja permite completar un ciclo de revisión sintético con trazabilidad.

### 75 · Ampliar informes de gestión
Define fuentes, cobertura y estados de confianza para cada indicador. Prueba exportación y comparación de snapshots. **Salida:** informes que distinguen dato consolidado, estimación y dato pendiente.

### 76 · Versionar reglas y fuentes
Asocia vigencia, fuente, versión y ámbito a cada regla. Prueba que un cálculo histórico se reproduce después de una actualización. **Salida:** diferencias auditables entre dos versiones y evidencia preservada.

### 77 · Ampliar fiscalidad por bloques
Elige un régimen y territorio por entrega. Delimita supuestos, entradas, casos límite, fuentes y revisión experta. **Salida:** fixtures positivos, negativos y casos excluidos antes de ofrecer una nueva capacidad.

### 78 · Evaluar localizaciones y addons
Compara versiones, mantenimiento, dependencias, licencia y compatibilidad con Community. Instala primero en una base sintética y ejecuta las pruebas afectadas. **Salida:** decisión específica por addon con evidencia.

### 79 · Separar preparación, emisión y presentación
Diseña fronteras de producto, permisos y responsabilidades para cada capacidad. Documenta qué controles y validación externa necesita cada fase. **Salida:** proyectos revisables con criterios independientes y alcance explícito.

### 80 · Diseñar banca y conciliación por fases
Empieza con un conjunto sintético de movimientos en lectura, después con propuestas explicables y revisión humana. **Salida:** reconciliación reproducible con referencias, conflictos y límites de ejecución definidos.

### 81 · Definir conservación y baja
Inventaría datos locales, referencias, adjuntos, auditoría y operaciones abiertas. Ensaya exportación y baja con una empresa ficticia. **Salida:** el operador puede explicar qué se conserva, exporta o desactiva y verificar la decisión.

### 82 · Preparar una demo repetible
Versiona fixtures, instrucciones de arranque, escenarios nominales y fallos deliberados. Incluye lectura, revisión humana e incertidumbre sin credenciales reales. **Salida:** otra persona puede reproducir la demo y comparar los resultados con la matriz esperada.

## Entrega para la revisión de mañana

- Deja el worktree limpio o identifica cualquier cambio sin commit que tenga que conservarse. Entrega nombre de rama, SHA final, base y enlaces a PRs.
- Enumera las tareas cerradas con evidencia y las pendientes con el primer paso para retomarlas. Indica qué se probó con dobles y qué se probó con Odoo real.
- Señala el primer fallo reproducible que quede, con comando, archivo, resultado observado y alternativa considerada.
- Resume cualquier cambio de contrato, migración, permiso, dependencia, workflow o archivo protegido. Incluye las decisiones que requieren revisión.
- Para la revisión del 11 de noviembre, el orden es **diff y seguridad → evidencia de laboratorio → regresión de cierre y reconciliación → simulación de Agente → decisión sobre la siguiente ola**.
