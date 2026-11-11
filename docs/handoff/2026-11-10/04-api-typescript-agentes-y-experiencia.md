# 04 · API, SDK TypeScript, agentes, eventos y experiencia humana

Fecha: 2026-11-10. Este documento sirve a la IA que conecte Gestoría con la plataforma del propietario. La integración concreta en `uniscrolliabrain-cloud/agente` no se ha aplicado y requiere su aprobación expresa. No interpretar la existencia de un SDK o una tabla de roles como un Organizational Runtime ya instalado.

## Arquitectura de consumo

La cadena prevista es AgntiaPro, runtime autenticado, cliente TypeScript/Hono, FastAPI Gestoría y Odoo Community propio. Las credenciales residen en servidor. El navegador recibe datos y acciones permitidas, no tokens ERP, certificados fiscales o un owner universal reutilizable. Las herramientas de modelos usan capacidades nominadas y no un proxy de métodos arbitrarios.

El paquete TypeScript existente se llama `@agntia/gestoria`. Conserva exports anteriores y añade subpaths `/odoo` y `/odoo-agent-tools`. El build genera JavaScript en dist y se acompañan declaraciones de tipos en types. El root del repositorio es un paquete Python: no instalarlo en pnpm como si su raíz contuviera el package.json del SDK.

El procedimiento de integración consiste en empaquetar el subdirectorio typescript y añadir su tarball al proyecto consumidor, o utilizar la receta equivalente documentada. El servicio Python se instala y arranca aparte. No consta publicación npm/PyPI durante esta entrega. Hono es peer opcional y la versión Node requerida por el paquete debe verificarse antes de ejecutar el build que elimina tipos.

## Contratos y errores

Los contratos Python viven en integrations/contracts.py y los tipos nuevos en typescript/odoo.ts/types/odoo.d.ts. Se usan IDs locales hex32, remotos enteros positivos, hashes y claves limitadas. Los DTOs rechazan campos desconocidos y cantidades no finitas en sus fronteras definidas. La validación runtime del SDK complementa, no sustituye, la del servicio.

Los errores públicos usan code, message, correlation_id, retryable y reconciliation_required. El cliente normaliza fallos para que la UI pueda distinguir autenticación, validación, conflicto, dependencia y proveedor caído sin mostrar un traceback remoto. Una operación HTTP200 puede contener un resultado de negocio reconciliation_required: el frontend no debe pintarla como ejecutada definitivamente.

Los documentos de contratos y el código son la fuente exacta de rutas disponibles. Algunos DTOs describen estructuras auxiliares y no implican que exista una ruta para cada modelo. No generar una UI desde nombres supuestos o ejemplos de otra versión de Odoo. Los métodos SDK deben revisarse junto con respuestas reales antes del wiring final.

## API de negocio existente

El prefijo es `/api/companies/{cid}/integrations/odoo`. Hay alta, validación y desactivación de conexión; health/capabilities; preview/import asíncronos; consulta de jobs, staging y conflictos; resolución humana; propuesta de contacto y factura borrador; aprobación; commit; conciliación; metadatos/descarga de adjuntos; clasificación humana; integridad de auditoría, métricas, eventos y briefing.

La API no expone una ruta POST/odoo/model/method. Hono filtra las rutas Odoo mediante allowlist exacta de método y path, además de los controles del backend. Una ampliación futura debe añadir explícitamente una capacidad y sus permisos; no relajar el prefijo entero para resolver un endpoint faltante.

La clasificación de un registro importado exige humano, documentos y revisión esperada. Vuelve a dejarlo unverified; el flujo de review original es otro acto. Si el origen era draft se exige confirmación de evidencia suficiente, pero un booleano enviado por un bot no sustituye el rol humano comprobado. La prueba sintética de ese recorrido no acredita que un PDF ficticio constituya emisión real.

## Secuencia correcta para importar

El cliente pide preview con resource partners o invoices, full según necesidad e idempotency_key. La API responde202 y job_id. El worker procesa la extracción; la UI consulta el job y muestra estados, advertencias y staging. La aceptación usa una segunda operación de importación con IDs de staging y otra identidad estable de negocio.

No bloquear una petición Hono esperando toda una sincronización. No interpretar la creación de un job como importación completada. Si cambia la fuente entre preview y aceptación, el backend puede bloquear; el cliente debe pedir actualización y explicar el conflicto, no reintentar con datos alterados automáticamente.

Una lista de staging puede contener PII autorizada. No volcarla completa a logs o a un prompt de diagnóstico. Los IDs de empresa y scope se obtienen de sesión/gateway verificados, aunque la herramienta del agente reciba referencias a objetos para proponer trabajo.

## Secuencia correcta para una escritura

El agente prepara una propuesta mediante dry-run. La UI muestra diff, destino, totales, caducidad, origen y bloqueos. Un humano autorizado revisa y aprueba el hash exacto. El commit usa proposal_id, approval_id, expected_revision e idempotency_key. Cambiar la propuesta exige aprobación nueva; cambiar de clave no permite ejecutar dos veces una propuesta.

Ante timeout o resultado incierto se conserva la clave original y se consulta conciliación. No ocultar el problema creando otra propuesta equivalente ni decir «falló» como si fuera seguro que el backend no escribió. El resultado remoto debe comprobar compañía, tipo, ID, estado draft y totales cuando corresponde.

La interfaz necesita distinguir propuesto, aprobado, ejecución pendiente, completado, bloqueado y pendiente de conciliación. No anticipar estados en el chat sin recibirlos del backend. En la versión actual no hay herramienta de emisión fiscal; un botón nuevo no puede saltarse las guardas de publicación.

## Roles agénticos previstos

Laia supervisa, prioriza y comunica hechos; Juan prepara gestoría y excepciones; Antonio analiza finanzas; Marco ejecuta SOP autorizados. Ana y Pedro se reservan para ámbitos laborales/seguridad cuando haya capacidades y políticas definidas. Ninguno obtiene autorización por su nombre o avatar. El principal autenticado, tenant, empresa, rol y capacidad son los que mandan.

Las tools actuales permiten salud, preview/import, estado, staging/conflictos, propuestas y briefing. No permiten approve, commit, clasificación fiscal humana ni un ejecutor universal. Los métodos humanos pueden existir en el SDK para UI/servidor, sin entregarlos al catálogo de herramientas del modelo.

Conectar Laia no significa dotarla de una conversación ficticia que diga que revisó facturas. Debe consumir eventos/objetos reales, citar evidencia, identificar bloqueos y reconocer ausencia de datos. El costo o duración de trabajo debe proceder del runtime o de mediciones, no de narración inventada.

## Eventos y cadencia organizacional

Los eventos incluyen schemaVersion, source, tenantId, companyId, correlationId, causationId, fecha y payload de referencias. La API entrega pendientes y acepta ACK persistente. El consumidor debe guardar el evento y su efecto antes de confirmar. La entrega actual no conserva pendientes separados por cada avatar: el runtime puede distribuir a varios trabajadores una vez recibidos.

Las rotas diaria, semanal y mensual son un contrato de organización. Diariamente se revisa salud, datos nuevos, documentos y urgencias reales; semanalmente anomalías y pendientes; mensualmente cierre y preparación. La agenda se aloja en el runtime de AgntiaPro, no en un scheduler empresarial paralelo dentro de Gestoría.

La cadencia profesional no obliga a fingir horas de actividad si una operación termina en segundos. Hay que distinguir tiempo de máquina, agenda de supervisión y comunicación al owner. Toda tarea debe tener dueño, resultado, estado y fuentes.

## Experiencia de usuario objetivo

AgntiaPro deberá ofrecer una bandeja empresarial, documentos, ventas, gastos, caja, informes, expedientes y aprobaciones. El chat permite pedir trabajo y entender datos; las pantallas permiten revisar y editar con precisión. El cliente no necesita entrar en Odoo para el recorrido normal, aunque el equipo interno conserve acceso administrativo restringido.

La UI debe ser adaptable a móvil, mantener contexto de empresa y mostrar cuándo un resultado quedó desactualizado. En una propuesta de factura deben verse emisor, receptor, líneas, impuestos, moneda y efecto esperado. En un informe deben verse periodo, origen y frescura. Una aprobación no debe quedar oculta tras un mensaje genérico de «aceptar».

La experiencia de edición conversacional de Agntia-video fue un antecedente de esta filosofía, no una implementación transferida literalmente. El dashboard actual de Gestoría tiene pruebas de navegador; no equivale a todas las nuevas pantallas de CRM, bancos o RR.HH. descritas en la visión. Cada futura pantalla necesita su recorrido y validación.

La próxima IA debe entregar primero un wiring propuesto, DTOs y ejemplo de consumidor con credencial acotada, y aplicarlo en `agente` solo dentro de autorización expresa. Verificar errores, revocación, aislamiento, eventos repetidos y edición concurrente, además del caso feliz. Así humanos y agentes podrán compartir operaciones sin compartir privilegios indiscriminadamente.


## Fuentes internas para continuar

- [Rutas de negocio](../../../agntia_gestoria/integrations/odoo/routes.py).
- [SDK Odoo](../../../typescript/odoo.ts).
- [Tools agénticas](../../../typescript/odoo-agent-tools.ts).
- [Allowlist Hono](../../../typescript/odoo-routes.ts).
- [Guía de integración](../../odoo-adapter/agent-integration.md).

Siguiente lectura: [índice y protocolo de uso](README.md). La evidencia se atribuye al SHA/entorno descrito, no a cualquier checkout posterior.
