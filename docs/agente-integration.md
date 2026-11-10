# Campaña de integración de Gestoría con Agente y Odoo Community

Fecha de planificación: 10 de noviembre de 2026. Estado: propuesta de ejecución. La revisión documental no acredita una simulación, una instalación ni un piloto.

Esta campaña añade el itinerario de integración y sus criterios de salida al [contrato de ejecución Odoo C01–C20](odoo-adapter/CAMPAIGN.md). El [handoff de Windows](../HANDOFF-CODEX-WINDOWS.md) contiene las instrucciones del laboratorio. El [informe de estado](odoo-adapter/final-report.md) conserva los resultados ya observados. El [contrato propuesto en Agente](https://github.com/uniscrolliabrain-cloud/agente/blob/b37b67d/docs/07-integraciones/GESTORIA.md), idéntico al adjunto revisado, sirve de guía. Las decisiones de este plan precisan qué se adopta y cuándo.

## Objetivo y arquitectura

Agente autentica al actor y resuelve su tenant. Su servidor utilizará el SDK TypeScript para llamar al servicio Python de Gestoría, que aplica las políticas por empresa y conecta con Odoo Community 19 mediante un adaptador propio. Agente conserva la conversación, las vistas y la orquestación. Gestoría conserva el perfil fiscal, las revisiones, los cálculos y la procedencia de los datos normalizados. Odoo es la autoridad sobre los objetos ERP. Cada entidad tiene una autoridad declarada antes de habilitar su sincronización.

```text
Humano o runtime de Agente → SDK en servidor → API de Gestoría → adaptador → Odoo
Odoo → importación validada en Gestoría → cambios y lecturas de dominio → Agente
```

Durante la simulación, un consumidor externo usa el SDK empaquetado y los contratos de Agente fijados por commit. La segunda pasada utiliza una copia desechable del runtime con un punto de inyección de pruebas. El workspace oficial de Agente incorpora la dependencia después del gate de integración.

## Diagnóstico inicial

| Hallazgo de la revisión | Trabajo y evidencia exigida |
| --- | --- |
| En Gestoría, `agentTools` exporta `close_reviewed_case`. El endpoint de cierre exige revisión vigente, pero admite roles de escritura. | Restringir cierre a owner/reviewer en el servidor, retirar la herramienta automática y comprobar API directa, SDK y paso por Hono. Verificar que el circuito humano sigue funcionando. |
| Hono delega la resolución del cliente en el host y admite varias rutas de escritura bajo empresas. | Resolver identidad y binding en servidor. Exponer un catálogo explícito de operaciones por rol y probar acceso directo, credenciales revocadas y manipulación de rutas o IDs. Revisar anulación de registros como operación separada antes de exponerla al runtime. |
| La auditoría SQLite ya tiene secuencia y cadena hash por empresa. | Proyectar una lista explícita de eventos y campos. Usar la secuencia de commit como orden; la hora se conserva para visualización. Evitar ordenar el cursor por timestamps que pueden coincidir o llegar tarde. |
| El workspace de compras de Agente es un scaffold. El runtime ya mantiene contexto por tenant. | Usar el contexto autenticado existente y probar un adaptador estrecho. Las propuestas de ViewPlanner y nuevas vistas pertenecen a una ola posterior y requieren evidencia del flujo de datos. |
| C02 tiene evidencia estática. La instancia real y el transporte están pendientes. | Preparar C03 para cerrar las comprobaciones de runtime de C02. Separar la revisión de fuentes, los tests con dobles y la evidencia de Odoo real. |

## Etapa 1. Gestoría y laboratorio

| Ola | Fases | Entregable y salida |
| --- | --- | --- |
| 1A · Baseline | C01, verificación de C02 | Fijar commits de ambos repos, lock de Odoo e imagen o build con procedencia verificable. Ejecutar suite Python, build y empaquetado TypeScript, smoke HTTP y comprobar regresión del servicio sin Odoo. Conservar comandos, versiones y resultados. |
| 1B · Entorno | C03 y gate runtime de C02 | Arrancar Odoo y PostgreSQL en red aislada con dos DB sintéticas. Probar arranque, reinicio, restauración y configuración repetible. Registrar módulos efectivos, con y sin `account`, e incluir `l10n_es` donde corresponda. Verificar un bot mínimo y otro sin permisos, así como el contrato JSON-2 con la instalación concreta. |
| 1C · Contratos y permisos | C04–C06 | Inventariar rutas por rol. Cerrar bypasses, definir esquema de errores y compatibilidad aditiva. Probar migraciones con una copia de SQLite previa, reapertura y recuperación tras interrupción. Referenciar secretos desde configuración de servidor y comprobar revocación y redacción. |
| 1D · Conexión y aislamiento | C07–C09 | Validar versión, DB, compañía, modelos, campos y ACL. Derivar el binding tenant → empresa Gestoría → conexión/DB/compañía Odoo desde configuración autorizada. Denegar antes de llamar a Odoo si el binding es ambiguo. Probar dos tenants, dos DB, compañías hermanas y contactos globales. |

**Gate G1.** Baseline reproducible, permisos humanos aplicados por el servicio y evidencia real del aislamiento. Una capacidad ausente, insuficiente o desconocida se informa como tal. Un fallo de aislamiento bloquea la salida.

## Etapa 2. Flujos y consistencia del middleware

| Ola | Fases | Entregable y salida |
| --- | --- | --- |
| 2A · Lectura | C10–C11 | Leer contactos y después facturas de prueba, paginados y acotados al binding. Registrar modelo/ID, conexión, empresa, actualización de origen, captura, hash y ejecución de sync. Verificar ausencia de facturas al faltar `account`, estados y rectificativas con fixtures explícitos. |
| 2B · Importación | C12–C14 | Previsualizar el mapeo, importar como `unverified`, preservar revisión humana y señalar preparaciones obsoletas. Repetir lote y reiniciar a mitad sin perder ni duplicar registros. Guardar evidencia de procedencia y aplicar política de adjuntos con hashes y alcance por empresa. |
| 2C · Escritura controlada | C15–C17 | Primero un contacto sintético desde un comando de origen de Agente. Guardar intención y correlación, mostrar dry-run y ligar aprobación humana a su hash. Simular timeout tras commit, caída del worker y concurrencia. Añadir borradores Odoo solo tras demostrar reconciliación. Evaluar addon si la instancia no ofrece una forma fiable de identificar o ejecutar la operación en una sola transacción. |
| 2D · Contrato para consumidor | C18 | Publicar métodos tipados para estado, contactos normalizados, registros, preparaciones, casos, dashboard y cambios según el alcance de cada flujo. Probar instalación desde el paquete construido en un proyecto temporal y compatibilidad con llamadas actuales. |

**Gate G2.** Hay un flujo de lectura y un flujo de escritura aprobada verificados contra Odoo real. La misma operación concurrente o reentregada produce un efecto. Si no se puede verificar el resultado remoto, queda pendiente de reconciliación y se bloquea la repetición automática. Facturas en borrador, adjuntos y vistas se aceptan por capacidad, con sus pruebas y sus propios estados.

### Decisiones de contrato

- **Estado y frescura.** Separar disponibilidad del servicio, capacidades y sincronización por empresa. Usar `live | recent | stale | unknown` con umbrales documentados y reloj controlable en tests. Añadir metadatos sin cambiar la forma de respuestas antiguas; si una ruta devuelve un array, usar otra representación o una versión explícita para el envelope.
- **Feed.** Cursor opaco vinculado a empresa y versión. Proyectar auditoría por secuencia estable con límite y retención definidos. Persistir el checkpoint al confirmar el procesamiento; deduplicar por ID estable de evento. Si expira el cursor, indicar cómo reconstruir la proyección. Probar eventos concurrentes, páginas vacías, reentrega y cursor de otra empresa. Si el evento de dominio y la auditoría no se confirman juntos, cerrar esa brecha antes de confiar en el feed.
- **Idempotencia.** Distinguir la referencia de un objeto remoto de la clave de una petición de escritura. Para una misma clave y contenido, recuperar el resultado previo o su estado; para contenido distinto, devolver conflicto. Mantener el 409 de registros económicos duplicados y reconciliarlo mediante la referencia original. Probar timeout antes y después del commit.
- **Errores.** Distinguir validación, autenticación, permisos, conflicto, capacidad ausente, indisponibilidad y resultado desconocido. Una escritura con respuesta ambigua queda en reconciliación. Una lectura recuperable puede reintentarse con límite. La UI recibe procedencia, frescura y un estado accionable; las filas de Odoo y las credenciales quedan del lado del servicio.

## Etapa 3. Simulación previa a la integración

| Ola | Fases | Ejecución |
| --- | --- | --- |
| 3A · Simulación de contrato | Preparación de C19 | Crear un harness reproducible fuera del checkout oficial de Agente. Fijar versiones del SDK y contratos del consumidor. Usar dobles para errores, reloj, paginación, revocación y caídas. Comprobar que una operación de agente no puede revisar ni cerrar, aun con un expediente aprobado por un humano. |
| 3B · Ensayo con runtime y servicios reales | C19 y verificación previa de C20 | Ejecutar el runtime de una copia desechable de Agente con un tenant y un actor sintéticos. Recorrer lectura de contacto, comando de contacto aprobado, importación de un dato ERP y consumo de un cambio con frescura. Probar la frontera entre tenants, una herramienta fuera de catálogo, caída de Gestoría, timeout posterior al commit Odoo y reinicio con reentrega. Usar decisiones de prueba explícitas; medir por separado una ejecución determinista y cualquier narración de Laia que se pruebe. |
| 3C · Diagnóstico y cierre | Cierre de simulación | Entregar matriz esperado/observado, trazas sanitizadas, versiones, responsables y fixes por hallazgo. Corregir en el repositorio responsable, reconstruir el paquete y repetir el caso fallido más la matriz de regresión. Medir latencia y recuperación con carga declarada y fijar los umbrales del piloto a partir de esa evidencia. |

**Gate G3, previo a incorporar el SDK en Agente.** El mismo par de commits supera el harness y el ensayo con servicios reales. Cada hallazgo que afecte seguridad, aislamiento, revisión humana, duplicados, pérdida de datos o recuperación debe quedar corregido y vuelto a probar. Los demás requieren decisión explícita, responsable y criterio de seguimiento. Registrar cada caso como PASS, FAIL, BLOCKED o NOT VERIFIED con evidencia enlazada. Un caso obligatorio pendiente bloquea la integración. Presentar el diagnóstico y la PR revisable antes de la incorporación definitiva.

## Etapa 4. Incorporación y piloto

1. **Ola 4A · PR en Agente.** Fijar la versión del SDK, registrar herramientas en el servidor con allowlist y resolver el cliente desde el actor autenticado. Usar el runtime y scheduler existentes. Activar mediante flag por tenant, inicialmente apagado. Ejecutar pruebas de runtime, aislamiento y regresión de conversación y herramientas.
2. **Ola 4B · Primer tenant piloto.** Activar lectura primero. Validar datos normalizados y estados degradados en dashboard, registros o expediente. Introducir el feed en las vistas solo después de demostrar persistencia del cursor y reconciliación. Habilitar una escritura aprobada como capacidad independiente si supera G2 y G3.
3. **Ola 4C · Aceptación C20.** Probar instalación limpia, recuperación desde backup, reversión del flag, apagado de nuevas escrituras y reconciliación de las pendientes. Completar E2E A–E del handoff y entregar runbook con configuración, trazas, alertas, responsables y procedimiento de desactivación.

**Gate G4.** La PR supera CI y el piloto cumple los umbrales acordados. Una fuga entre tenants, un bypass de revisión, un secreto expuesto o un efecto ERP duplicado detiene el piloto. Para revertir, desactivar herramientas y nuevas escrituras, conservar estado de operaciones y reconciliar las pendientes con intervención autorizada. Evitar restauraciones destructivas como mecanismo de reversión de una operación ERP.

## Evidencia y seguimiento

Cada fase CNN conserva su rama y PR según el contrato de ejecución, con README, EVIDENCE, TESTS, RISKS y decisiones. Cada prueba registra ID, fase, commits, módulos y versión Odoo, actor y tenant sintéticos, pasos reproducibles, resultado esperado, observado y enlace a evidencia. Las credenciales se inyectan durante ejecución y las trazas publicadas se sanitizan. Una simulación con dobles acredita el contrato simulado. La instalación, las ACL y las transacciones de Odoo se acreditan con la instancia real.

La primera entrega de ejecución es el laboratorio de C03 y la verificación runtime pendiente de C02. Esta revisión documenta hallazgos estáticos y criterios de aceptación. Sus olas de implementación y simulación quedan pendientes.
