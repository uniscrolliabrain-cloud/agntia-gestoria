# Campaña de ejecución · RR. HH. agéntico con Anam

Documento de trabajo para agentes implementadores. Corte de investigación del 10 de noviembre de 2026. Alcance inicial para pymes españolas y Odoo Community 19. El producto es un asistente de RR. HH. con voz y vídeo que prepara trabajo verificable, sigue las tareas abiertas y entrega resultados o decisiones listas para una persona autorizada. El portal escrito comparte las mismas operaciones y el mismo expediente que el avatar.

## Decisión de arquitectura

Agente conserva conversación, sesión autenticada, selección de herramientas y presentación. Gestoría gobierna procesos de negocio, permisos, reglas, trabajos persistentes, evidencia, aprobaciones y reconciliación. Odoo conserva los registros operativos elegidos. Anam es la interfaz de conversación audiovisual. Un proveedor laboral puede ser autoridad sobre el cálculo y la emisión de nómina. El avatar identifica su naturaleza de IA. La sesión de vídeo puede terminar mientras el trabajo continúa en Gestoría.

El mismo snapshot y versión de política deben reproducir la misma decisión de dominio. Fija además el periodo, zona horaria, calendario, unidad de tiempo y versión del normalizador. Separa en pruebas la decisión pura y los efectos externos. En producción, una repetición devuelve el trabajo existente o abre una revisión explícita si cambió el origen.

| Repositorio o producto | Decisión | Criterio de incorporación |
| --- | --- | --- |
| Odoo Community 19 | Instalar en el servidor Odoo los addons hr, hr_attendance y hr_holidays para el primer recorrido. Añadir hr_recruitment y hr_expense en sus olas. | Verificar los manifiestos contra el SHA que construye el laboratorio existente, dependencias, ACL, cambios de versión de empleado y datos de actualización. Instalar por lista cerrada y conservar el lock. [Código oficial](https://github.com/odoo/odoo/tree/19.0/addons) |
| OCA/hr-holidays | Candidatos concretos hr_holidays_public y hr_holidays_natural_period. El segundo únicamente si una política aprobada requiere días naturales. | La rama 19.0 lista ambos. Instalar en base desechable y probar calendario por centro, solapamiento y compatibilidad de upgrades. [Rama 19.0](https://github.com/OCA/hr-holidays/tree/19.0) |
| OCA/hr y OCA/hr-attendance | Evaluar addons puntuales cuando el fixture muestre una brecha. Investigar planificación de calendarios y conciliación de fichajes. | Comprobar que el addon está fusionado en 19.0, leer manifiesto, licencia, dependencias y estado de CI. Una PR de migración abierta se registra como pendiente. [OCA HR](https://github.com/OCA/hr) · [Migraciones de asistencia](https://github.com/OCA/hr-attendance/milestone/7) |
| OCA/payroll y localización española | Experimento separado. La primera entrega exporta incidencias a asesoría o proveedor de nómina e importa confirmaciones y recibos. | OCA publica un motor 19.0. Exigir evidencia de reglas, integraciones, mantenimiento y validación laboral española antes de optar por cálculo propio. [OCA Payroll](https://github.com/OCA/payroll/tree/19.0) · [OCA España](https://github.com/OCA/l10n-spain) |
| Frappe HR | Estudiar modelos de turnos, onboarding, desempeño y portal como referencia funcional. Evaluar su operación como servicio únicamente si cubre una brecha prioritaria con un coste justificable. | En un ensayo aislado medir dependencias operativas, aislamiento, APIs y fuente de verdad. Extraer conceptos y especificaciones propias. Cualquier reutilización literal requiere revisión de licencia, atribución y compatibilidad. [Frappe HR](https://github.com/frappe/hrms) · [Licencia](https://github.com/frappe/hrms/blob/develop/license.txt) |
| Google OR-Tools | Candidato para planificar turnos cuando restricciones y tamaño hagan insuficiente una propuesta basada en reglas. | Usar como dependencia fijada del proceso de planificación. Medir restricciones duras, tiempos límite y reproducibilidad del plan publicado. [OR-Tools](https://github.com/google/or-tools) · [Ejemplo de planificación](https://github.com/google/or-tools/blob/stable/examples/python/bus_driver_scheduling_sat.py) |
| Anam SDK y Cookbook | Instalar @anam-ai/js-sdk en el paquete web de agente para la prueba de vídeo. Usar el Cookbook como referencia de integración y autenticación. | Verificar API soportada, versión fijada, accesibilidad, recuperación, límites, coste por sesión y condiciones de tratamiento. Elegir integración con modelo propio o pasarela autenticada según la prueba, manteniendo Agente como orquestador. [SDK](https://github.com/anam-org/javascript-sdk) · [Cookbook](https://anam.ai/cookbook) · [Herramientas autenticadas](https://github.com/anam-org/anam-cookbook/blob/main/content/recipes/ephemeral-webhook-tools.mdx) |
| Factorial | Referencia de experiencia y cobertura de producto. Implementar flujos y experiencia propios. | Comparar jornadas, ausencias, turnos, selección, onboarding, desempeño, documentos, gastos e incidencias de nómina por resultado observable. [Catálogo](https://factorial.es/funcionalidades) · [Guía](https://factorial.es/ebooks/guia-uso-funcionalidades-factorial) |

La investigación verifica la existencia pública y la disponibilidad declarada de los candidatos señalados. La instalación y los permisos reales de cada addon de RR. HH. quedan como evidencia de la campaña. Para cada dependencia crea una ficha con origen, versión y SHA, licencia de su manifiesto, dependencias transitivas, mantenedor, motivo, casos cubiertos, upgrade, rollback y prueba real. La primera entrega requiere el SDK de Anam y los tres addons Community citados. Las extensiones OCA se incorporan cuando un caso concreto las justifica.

## Organización de la ejecución

- Parte de main actual en Gestoría y Agente. Consulta el [handoff Freebuff](handoff-freebuff-2026-11-10.md), comprueba los estados de las [PR #4](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/pull/4), [#11](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/pull/11) y [#12](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/pull/12) y registra los SHA realmente usados. Aprovecha el laboratorio, SDK, worker y simulador cuando su estado y contratos lo permitan. La revisión local de Agente en el checkout disponible no encontró coincidencias de Anam en apps ni packages. Vuelve a buscar en la revisión que se ejecute.
- Crea una rama y un worktree por frente. Usa rrhh/01-laboratorio, rrhh/02-runtime, rrhh/03-portal-anam y rrhh/04-evaluaciones como nombres orientativos. Desde cada clon ejecuta git fetch origin y git worktree add -b NOMBRE RUTA SHA_BASE. Verifica estado limpio y registra base y dependencia en cada PR. Si dos PR cambian un contrato, publica primero su esquema y fixtures, y fija la revisión consumida en la segunda.
- Los agentes pueden trabajar en paralelo en investigación de addons, núcleo de Gestoría, integración audiovisual y evaluaciones. Asigna a cada tarea un repositorio y dueño. Evita editar el mismo contrato desde dos frentes. Un agente de integración reúne cambios en una rama temporal y ejecuta la matriz conjunta.
- Cada tarea entrega diff, comandos, fixtures, resultado esperado y observado, SHA, enlace de CI y estado PASS, FAIL, BLOCKED o NOT VERIFIED. Distingue mocks, Odoo real, Anam real y pruebas con personas. Un fallo de aislamiento, aprobación o duplicación bloquea el flujo afectado hasta reproducirlo y corregirlo.
- Alcance de datos inicial sintético. Las pruebas con personas y proveedores reales requieren un entorno designado, configuración de acceso y tratamiento de datos aprobados por el responsable correspondiente.

## Etapa 0 · Descubrimiento y alcance

1. Dibuja los recorridos de dueño, responsable, empleado, operador laboral y asesoría. Para cada uno identifica entrada, fuente, decisión, evidencia, entrega y quién puede confirmar. Selecciona una pyme piloto con un calendario y una política revisada.
2. Define el primer encargo con una demo concreta. «Prepara el cierre de octubre». El asistente devuelve horas, incidencias accionables y un paquete de exportación tras la revisión aplicable. Usa un calendario sintético que incluya jornada parcial, turno nocturno, fichaje incompleto y ausencia.
3. Construye una matriz de capacidades por flujo. Marca nativo, addon, propio, proveedor y pendiente de verificación. Contrasta versiones Odoo 19 por manifiesto y ejecuta una prueba de instalación para cada candidato que vaya al piloto.
4. Fija las autoridades por entidad. Empleado, fichajes y ausencias en Odoo. Snapshot, incidencia, trabajo y aprobación en Gestoría. Identidad autenticada y conversación en Agente. Resultado de nómina en el proveedor. Un conflicto de fuentes se presenta con procedencia y responsable.
5. Especifica los datos que puede leer cada rol y qué entra al modelo, a Anam y a las trazas. Define conservación y acceso del registro horario a partir del art. 34.9 y valida la configuración con asesoría laboral. Revisa el tratamiento laboral y la clasificación de cada función de IA antes de activar selección o evaluación. El alcance inicial usa asistencia administrativa y revisión humana de decisiones de empleo. Excluye inferencia emocional de voz o vídeo en el trabajo y muestra identificación de IA en la sesión. [Estatuto de los Trabajadores](https://www.boe.es/buscar/act.php?id=BOE-A-2015-11430#a34) · [Guía AEPD](https://www.aepd.es/sites/default/files/2021-05/la-proteccion-de-datos-en-las-relaciones-laborales.pdf) · [Reglamento europeo de IA, arts. 5 y 50 y anexo III](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)

**Salida:** matriz de alcance y fuentes, roles, fixtures y una demo definida antes de cablear el avatar.

## Etapa 1 · Scaffolding y laboratorio

1. Identifica puntos de entrada del adaptador, migraciones, SDK, worker y CapabilityRunner en los SHA fijados. Anota qué componentes reutilizas y qué interfaces necesitan extensión. Ejecuta sus pruebas base antes de introducir módulos laborales.
2. Extiende el laboratorio sintético con dos tenants, compañías separadas, roles diferenciados y un bot Odoo por alcance. Incluye un fixture de compañías hermanas en la misma base. Si un addon falta, registra capacidad no disponible y verifica la degradación del resto.
3. Añade configuración versionada y flag de RR. HH. por tenant. Fija el catálogo de herramientas del backend y prepara scripts de arranque, carga y limpieza de fixtures sintéticos. Guarda credenciales en configuración privada y publica únicamente resultados sanitizados.
4. Crea esquemas de empleado mínimo, fichaje, ausencia, jornada esperada, incidente, cierre, aprobación y exportación. Usa IDs por ámbito y formato explícito de duración. Separa metadatos de origen de los datos visibles para el usuario.
5. Añade CI de instalación limpia y comprobación de contratos. Ejecuta unit tests sin proveedor, integración con Odoo real y un smoke de SDK por separado. Mide el upgrade desde una copia anterior de Gestoría y verifica que el módulo se mantiene desactivado donde no se configuró.
6. Prueba rutas normales de API, worker y SDK. Registra health de servicio, proveedor y capacidades, con fallos diferenciados y una comprobación de trazabilidad entre ambos repositorios.

**Salida:** dos empresas sintéticas reproducibles, API y SDK arrancables, modelos validados y comprobación negativa entre tenants.

## Etapa 2 · Motor determinista de cierre

1. Implementa lectura acotada de calendarios, empleados, fichajes y ausencias. Resuelve empresa y periodo desde el contexto de servidor. Pagina de forma estable y detecta resultados fuera de ámbito antes de normalizarlos.
2. Persiste snapshot inmutable con IDs fuente, hash, timestamps, zona horaria, revisión de política y fecha de corte. Conserva el dato original autorizado y los campos necesarios para explicar cada incidencia.
3. Construye cálculo puro. Divide periodos en intervalos, trata cruces de medianoche, horario de verano, pausas, jornadas parciales y festivos. Distingue eventos duplicados, fichajes incompletos, ausencia aprobada y ausencia pendiente. Los intervalos ambiguos generan incidencia en vez de imputar horas.
4. Implementa máquina de estados con transiciones verificadas. Estados mínimos preparado, bloqueado, pendiente de revisión, aprobado, exportado y reconciliación requerida cuando corresponda. Persiste quién hizo cada transición, revisión, motivo y evidencia.
5. Expón operaciones cerradas para preparar, consultar incidencias, proponer corrección, solicitar revisión, aprobar, exportar y consultar resultado. Usa esquemas versionados, códigos de error explícitos y respuestas que identifican el siguiente paso permitido.
6. Liga aprobación a hash, tenant, revisión y actor autorizado. Si cambió el origen, reabre revisión. Una rectificación crea un nuevo registro y conserva el anterior. La exportación lleva clave estable y manifiesto de totales e incidencias.
7. Asegura idempotencia y recuperación del worker. Prueba concurrencia con la misma clave, conflicto con payload distinto, caída antes del commit y ACK perdido después. Reconciliación consulta la identidad persistida antes de repetir un efecto.
8. Entrega fixtures dorados con horas y motivos esperados. Cubre turno nocturno, dos cambios de horario estacional, vacío, duplicado, ausencia parcial, centro equivocado y edición tras aprobar. Compara resultados al repetir con el mismo snapshot.

**Salida:** cierre reproducible y exportación sintética única, con revisión y evidencia. El riesgo de reejecución observado en la simulación de Agente debe quedar cubierto antes de habilitarle una capacidad que produzca efectos externos.

## Etapa 3 · Herramientas, entrenamiento y evaluaciones

1. Define herramientas de intención laboral con entradas limitadas a periodo, identificador autorizado y filtros admitidos. Inyecta identidad y alcance desde el host. Incluye descripciones de cuándo llamarlas, estados esperados y ejemplos de uso correcto.
2. Prepara SOPs para cierre, seguimiento de incidencias y entrega a asesoría. Para cada uno define objetivo, precondiciones, secuencia, bloqueos, cuándo pedir un dato y cuándo entregar una revisión.
3. Registra ejemplos de conversaciones en español y trazas esperadas con datos sintéticos. Incluye peticiones incompletas, correcciones, dueño con dos empresas, empleado pidiendo la nómina de otra persona y gerente con acceso parcial.
4. Evalúa llamadas a herramientas y efectos, además del texto. Mide éxito del proceso, selección de herramienta, aclaraciones, citas a evidencia y cumplimiento de revisión. Los casos de acceso ajeno o mutación sin autorización requieren cero efectos.
5. Prueba instrucciones incrustadas en notas, documentos o nombres. Verifica que su contenido se trata como datos. La suite debe detectar afirmaciones de éxito sin resultado confirmado y reintentos de estado incierto.
6. Versiona SOPs, esquemas, ejemplos y evaluaciones. Ejecuta regresión al cambiar modelo, instrucciones, versión del SDK o contrato. Considera entrenamiento adicional a partir de errores persistentes medidos. Usa datos sintéticos o autorizados y revisados para esa finalidad.

**Salida:** el agente demuestra que sabe iniciar, reanudar, escalar y entregar un cierre sin inventar horas, permisos o aprobaciones.

## Etapa 4 · Anam y portal

1. Haz una prueba audiovisual con una sesión autenticada de Agente. Emite token efímero del lado servidor ligado a sesión y usuario. Guarda la clave del proveedor en servidor. Verifica expiración, reconexión y cierre de sesión.
2. Compara dos integraciones soportadas. Modelo propio en Agente con avatar como presentación, o herramienta de Anam que llama a una pasarela autenticada. Mide tiempo hasta primera respuesta, interrupción, fidelidad del contexto, coste y facilidad para volver a texto. Documenta la elegida con una traza real.
3. En cada llamada valida sesión y alcance en servidor. Reutiliza IDs de trabajo y claves de deduplicación. Los resultados de Anam o del navegador nunca conceden permisos. Las aprobaciones con efectos se confirman en una pantalla autenticada que muestra la revisión exacta.
4. Presenta estado del trabajo, evidencia, incidencias y decisiones pendientes en el portal. El avatar resume y abre la vista correspondiente. Los datos sensibles se muestran solo al actor autorizado y se omiten del diálogo audiovisual por defecto.
5. Prueba micrófono denegado, silencio, interrupción, desconexión, doble clic, cambio de tenant y caída de Anam. Ofrece continuidad por texto con el mismo expediente. Valida teclado, subtítulos y manejo de errores sin bloquear el trabajo.
6. Verifica condiciones de Anam para grabaciones, retención, ubicación, transferencias, subencargados y contratos antes de enviar datos laborales reales. Desactiva grabación y minimiza transcripciones en el piloto según las capacidades y configuración comprobadas. Mide coste y duración de sesión con trazas sintéticas.

**Salida:** dueño autenticado inicia el cierre por vídeo, puede continuar por texto y recibe el mismo resultado verificable sin repetir la operación.

## Etapa 5 · Ampliación por módulos

1. Ausencias y vacaciones. Solicitud, saldo, sustitución y aprobación. Prueba calendario, solapamiento, revocación y privacidad del motivo. Entrega historial accesible al empleado y vista acotada al responsable.
2. Turnos. Empieza con plantillas, cobertura y cambios publicados con revisión. Modela restricciones duras y preferencias. Evalúa OR-Tools solo si la matriz lo justifica. Prueba cuadrante imposible, sustitución y cambios después de publicación.
3. Incorporación y salida. Usa plantillas de tareas, responsables, vencimientos y documentos. Prueba que un alta o baja reintentada conserva un único expediente y que se revocan accesos según el flujo aprobado.
4. Selección. Usa vacantes, entrevistas, comunicaciones preparadas y checklist. Separa expedientes de candidatos de los de empleados. Cualquier ranking, evaluación o recomendación de contratación exige revisión específica del uso de IA y controles antes de ampliarse.
5. Documentos y firma. Implementa expedientes, permisos, caducidad, confirmación de lectura y conexión con proveedor de firma. Prueba acceso ajeno, firma caducada y documento reemplazado después de solicitar firma.
6. Gastos. Recoge justificantes, detecta duplicados, aplica política versionada y prepara reembolso para revisión. Prueba extracción errónea y doble envío. Registra las consecuencias contables confirmadas por el proveedor correspondiente.
7. Nómina. Exporta incidencias aprobadas con formato versionado, acuse y conciliación de totales. Importa resultados en un circuito separado con permisos y cifrado. Prueba corrección fuera de plazo y reenvío tras fallo. Evalúa cálculo propio como proyecto independiente.
8. Desempeño y formación. Empieza por agenda, formularios, objetivos registrados y recordatorios. Prueba visibilidad de comentarios y alcance de responsables. Valida separadamente cualquier clasificación o decisión asistida.
9. Informes y seguimiento. Construye panel con frescura y evidencia, además de tareas proactivas por vencimiento. Reutiliza el scheduler de Agente para seguimiento de encargos y los trabajos de Gestoría para ejecución de dominio. Prueba duplicados, retrasos y reanudación.

**Salida por módulo:** una persona autorizada recibe el trabajo preparado, con evidencia, permisos probados, incidencias y acciones siguientes. La paridad se mide por recorridos terminados y revisados.

## Etapa 6 · Hardening, refactoring y operación

1. Ejecuta matriz de permisos por API, SDK, voz y worker. Cruza actor, empresa, sesión, referencia y credencial. Prueba una baja de permisos mientras la tarea está en curso y comprueba alcance antes del efecto.
2. Revisa secretos y datos en navegador, prompts, transcripciones, audio, trazas, exportaciones y backups. Usa centinelas sintéticos. Ensaya rotación, expiración, revocación y borrado donde aplique.
3. Ejecuta pruebas de concurrencia, reentrega, replay, pérdida de ACK, interrupción de worker y degradación del proveedor. Observa estado de cola y correlación entre Agente, Gestoría y Odoo.
4. Mide latencias p50 y p95 de conversación y herramientas, cola, errores por capacidad, coste por tarea, tasas de intervención humana y tiempo de resolución. Fija umbrales de piloto sobre medidas reales y conserva tamaño de muestra.
5. Ensaya restauración conjunta de Gestoría y Odoo, adjuntos, referencias a secretos y ledger. Comprueba lectura y reconciliación tras restore. Registra tiempos y pérdidas toleradas según el objetivo acordado.
6. Refactoriza después de capturar comportamiento. Extrae reglas puras y adaptadores repetidos, unifica errores cuando coincida su semántica y conserva esquemas públicos. Haz PR pequeña por frontera y repite fixtures dorados y pruebas de replay.
7. Revisa dependencias y licencias con inventario de componentes y actualización reproducible. Prueba migraciones forward, recuperación con backup y desactivación por tenant. Evita un fork de Odoo cuando un addon aislado satisface el caso.
8. Redacta runbooks para corte de proveedor, identidad errónea, credencial revocada, expediente incoherente, fallo de Anam y efecto incierto. Valídalos con una persona que no haya escrito el código.
9. Ejecuta piloto de lectura, después de preparación y finalmente de una operación aprobada con efecto acotado. Compara entrega del agente con el trabajo revisado por el operador. Detén el flujo afectado si una prueba crítica falla y conserva capacidad de recuperar operaciones pendientes.
10. Publica matriz de entrega con flujo, repos y SHA, pruebas reales, limitaciones, responsables y criterios de ampliación. La experiencia de vídeo, la corrección del expediente y la seguridad de los efectos se aceptan por separado.

## Primera entrega para revisión

Entrega una demo reproducible del cierre sintético con 2 tenants, 3 roles y al menos 1 excepción por resolver. Incluye snapshot y versión de reglas, conversación y llamadas esperadas, evidencia de acceso ajeno denegado, cambio de origen tras la aprobación y replay de resultado incierto. Presenta el flujo por texto y el smoke audiovisual con Anam. Si el proveedor no está configurado, entrega las pruebas de contrato y registra el smoke real como pendiente. El informe debe identificar qué trabajo hizo el agente, qué verificó Gestoría y qué recibió la persona.
