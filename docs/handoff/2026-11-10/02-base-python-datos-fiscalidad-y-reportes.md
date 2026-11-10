# 02 · Base Python, persistencia, fiscalidad, documentos y reportes

Fecha: 2026-11-10. Parte del relevo documental. Este documento explica el núcleo que el adaptador debe preservar. No amplía el alcance legal de los motores ni acredita que todos los casos de una empresa española estén cubiertos. Leer el código y sus pruebas antes de cambiar una fórmula, un estado de revisión o una política territorial.

## Mapa inicial del paquete

El paquete Python `agntia_gestoria` usa FastAPI, Uvicorn y modelos Pydantic. `app.py` contiene la factoría `create_app`; `cli.py` ofrece el arranque del servicio. `pyproject.toml` declara Python >=3.11, dependencias runtime, extras dev y descubrimiento de paquetes. Las dependencias de informes incluyen python-pptx y ReportLab. El adaptador añadió httpx y cryptography, además del entrypoint `agntia-gestoria-odoo-worker`.

No se ha convertido la aplicación en TypeScript. La integración con Hono consiste en consumir un servicio Python mediante un cliente servidor y capacidades de negocio. Instalar una librería en pnpm no sustituye ejecutar FastAPI, el worker o sus dependencias. Tampoco consta publicación de una release en PyPI/npm durante esta entrega: instalar desde checkout o empaquetar los artefactos correspondientes.

Los archivos principales preexistentes son models.py, storage.py, auth.py, tax.py, engines.py, rules.py, territories.py, analytics.py y report_routes.py. La UI estática vive en static. La integración nueva está en integrations y se registra de forma aditiva. Los datos de referencia legales tienen su archivo propio en data/legal_sources.json.

## Empresas, identificadores y datos declarados

Una empresa Gestoría tiene un identificador local hexadecimal de32 caracteres. No es el entero de res.company en Odoo ni su nombre de base. Cualquier código nuevo debe mantener explícita esa diferencia. Se recoge forma jurídica, territorio y hechos fiscales declarados; que una empresa se llame de determinada manera o tenga un NIF no basta para escoger un régimen o motor.

Los hechos fiscales son entradas de dominio. Importar una factura con un impuesto21% no demuestra que sea IVA deducible ni que su fecha relevante coincida con invoice_date. La deducibilidad, categoría, tratamiento y evidencia deben quedar pendientes cuando no se puedan justificar. El propietario quiere cubrir todo el territorio a futuro, pero las exclusiones actuales deben bloquear correctamente.

Una IA debe inspeccionar modelos y validaciones reales en vez de añadir campos libres desde prompts. Los modelos cerrados y Decimal ayudan a detectar entradas inválidas, aunque no reemplazan la validación profesional. Conservar moneda, origen, revisión y documento permite explicar después un cálculo o una discrepancia.

## Persistencia original y transacciones

`storage.py` usa SQLite con WAL. Las tablas base son companies, objects y audit. Los cuerpos se guardan como JSON canónico; objects conserva tipo, empresa y una clave única opcional. Las conexiones activan foreign_keys y la abstracción transaction abre BEGIN IMMEDIATE. El despliegue inicial no presupone un clúster distribuido ni múltiples réplicas escribiendo sobre almacenamiento de red.

Las funciones identifier, canonical, digest, uid y now constituyen utilidades importantes del contrato. Los hashes deben ser reproducibles, no depender del orden incidental de un diccionario o de una representación float diferente. Una migración debe preservar los objetos previos y la secuencia de auditoría; no rehacer una base vacía y llamarlo actualización.

El adaptador incorpora migraciones en integrations/migrations.py sin reescribir storage.py. Crea tablas adicionales bajo transacción y una copia SQLite anterior al DDL. Esa copia local no es por sí sola un backup completo del servicio: faltan ficheros, claves externas y, para Odoo, PostgreSQL/filestore. La validación de restauración operativa sigue pendiente.

## Autenticación y revisión humana

`auth.py` define Actor con id, rol y tuple de empresas. Las credenciales configuradas proceden de GESTORIA_ACTORS_JSON y del token owner; la autenticación compara secretos sin exponerlos como prueba de identidad en el body. Existen roles owner, reviewer, agent y viewer. company_access devuelve no encontrado para empresas fuera del scope, evitando revelar su existencia.

La base permite un owner local cuando no hay credenciales y la petición viene de loopback/testclient. El adaptador Odoo impone una condición adicional: ese principal local solo puede operar si ODOO_ALLOW_LOCAL_OWNER se habilita expresamente. No generalizar el fallback local a acceso remoto, jobs o gateway de producción.

Los expedientes siguen estados draft, in_review, reviewed y done con controles de revisión ligados al contenido. El estado done no demuestra presentación tributaria. Los registros fiscales también tienen revisión humana específica. Un agente puede preparar trabajo; no adquiere facultad de aprobar porque se llame Juan, Laia o supervisor. Proteger credenciales humanas sigue siendo responsabilidad del despliegue y del gateway.

## Registros económicos y cálculos fiscales

`tax.py` contiene TaxRecord, el alta de registros, revisión, unicidad por empresa/external_id y anulación interna. Los importes usan Decimal y campos explícitos de base, cuota, retención y deducibilidad. Una identidad externa ayuda a evitar duplicados pero no resuelve por sí sola actualización, rectificación o borrado remoto; esas políticas las añade la integración.

`engines.py` contiene motores303 y130 de2026 para supuestos concretos de territorio común. El plan no es usar un LLM para inventar casillas o inferir regímenes. Los modelos deben comprobar sus condiciones y rechazar casos no cubiertos. La renta anual, sociedades y cobertura de todos los territorios siguen siendo objetivos futuros, no capacidades presentes por extensión del nombre «gestoría».

La comparación con Holded no cambia esta realidad. Que otro producto tenga más modelos fiscales no autoriza a copiar una fórmula sin fuentes, tests de referencia y revisión. Toda ampliación debe identificar ejercicio, normativa, entradas, casillas, exclusiones, rectificativas y estado de aceptación. Un resultado de cálculo y un justificante oficial son objetos distintos.

## Borradores contables y de factura

Los borradores de factura locales calculan totales y mantienen estado que no acredita emisión fiscal. Los borradores de asiento comprueban debe/haber equilibrados. Ninguna de estas comprobaciones demuestra, por sí sola, selección correcta de cuenta, diario, fecha, secuencia o régimen fiscal.

El adaptador puede proyectar un invoice_draft a un account.move draft con configuración explícita y aprobación. En la versión actual no se publica, envía, paga ni presenta. Las equivalencias de estado entre sistemas deben conservarse; no devolver «factura emitida» porque exista un ID remoto. Las diferencias de redondeo o retención bloquean la proyección cuando no son compatibles.

Anular un registro interno no debe desencadenar unlink en Odoo. Una rectificación puede necesitar un procedimiento fiscal/contable distinto. Conservar el original, su revisión y sus documentos importa más que conseguir una tabla visualmente limpia eliminando historia.

## Auditoría, conflictos y frescura

La auditoría base encadena hashes por empresa. Cada entrada incluye actor, acción, objeto, content_hash y previous_hash. El nuevo verificador comprueba la cadena y enlaza evidencia de outbox. Esto detecta alteraciones según el modelo local; no convierte SQLite en un registro imposible de reescribir por un administrador comprometido. Un anclaje externo o custodia reforzada sería una ampliación futura.

Los cambios remotos no pisan registros revisados. El adaptador crea conflictos y marcadores económicos cero no verificados que cambian el fingerprint de datos utilizado por cálculos/reportes existentes. Así puede señalar resultados stale sin modificar fórmulas o analytics. El marcador es un mecanismo técnico de bloqueo/trazabilidad, no un ingreso o gasto nuevo que se pueda presentar.

Las decisiones keep_local y supersede_local deben conservar evidencia y explicación humana. La segunda anula localmente lo correspondiente y archiva enlaces antes de aceptar una nueva versión; nunca borra el movimiento del ERP. Si un cálculo previo era correcto con sus entradas, debe conservarse su snapshot y marcar que ya no representa el estado actual.

## Documentos, dashboard y entregables

La aplicación conserva documentos y genera informes a través de analytics/report_routes. Existen snapshots y salidas PDF, PPTX, HTML y SVG. La aspiración de infografías inteligentes se apoya en datos calculados y verificables; no en inventar cifras para rellenar una presentación.

Los adjuntos importados por Odoo se descargan explícitamente, se validan y se guardan cifrados mediante Fernet. El pequeño cambio de app.py permite servirlos con autenticación documental y comprobación de integridad. No se afirma que toda SQLite o los documentos históricos anteriores estén cifrados por esa función. Las claves deben recuperarse desde custodia externa; sobrescribirlas puede hacer ilegibles los originales.

La IA que continúe debe preservar fórmulas, reglas, territorios, fuentes y flujos de revisión. Si necesita modificarlos, justificar el alcance y añadir pruebas relevantes. Para una mejora meramente documental no hace falta repetir todas las suites: comprobar enlaces, baseline y diff es suficiente. Para una ampliación fiscal sí es obligatorio ejecutar los casos que demuestren el comportamiento y sus exclusiones.


## Fuentes internas para continuar

- [Servicio FastAPI](../../../agntia_gestoria/app.py).
- [Persistencia original](../../../agntia_gestoria/storage.py).
- [Motores acotados](../../../agntia_gestoria/engines.py).
- [Registros y revisión](../../../agntia_gestoria/tax.py).
- [Reportes](../../../agntia_gestoria/report_routes.py).

Siguiente lectura: [índice y protocolo de uso](README.md). La evidencia se atribuye al SHA/entorno descrito, no a cualquier checkout posterior.
