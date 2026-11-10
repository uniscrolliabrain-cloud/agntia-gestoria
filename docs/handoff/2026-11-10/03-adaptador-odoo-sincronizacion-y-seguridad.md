# 03 · Adaptador Odoo, sincronización, seguridad y escritura controlada

Fecha de corte: 2026-11-10. Este documento transfiere el diseño real del adaptador y los invariantes que otra IA debe conservar. Hay código y pruebas simuladas/CI; la instalación y los contratos con Odoo/PostgreSQL reales siguen pendientes de ejecución. No se debe marcar completa la seguridad del despliegue por leer este diseño.

## De la campaña C01–C20 a módulos concretos

La campaña original propuso numerosos nombres de archivo. La implementación consolidó funciones relacionadas en módulos cohesivos: Service concentra conexiones/binding; Imports concentra staging, cursores y conflictos; Commands reúne propuestas, aprobaciones y write-back; reads y mappers realizan extracción/normalización. No faltan capacidades únicamente porque no exista cada archivo sugerido. A la inversa, una carpeta con el nombre esperado no prueba funcionalidad.

El punto de composición es `integrations/odoo/adapter.py`. Las piezas comunes viven en integrations/contracts.py, errors.py, registry.py, policy.py y migrations.py. El router se registra desde app.py de forma aditiva; la feature flag ODOO_ADAPTER_ENABLED está desactivada por defecto. Desactivarla no implica borrar las tablas, enlaces o auditoría existentes.

La API objetivo es Odoo Community19 JSON-2. El upstream auditado se fijó en `60657b50d171ddf84ab58717fdee5ac26031065b`. Los ejemplos de otras versiones no son prueba de campos, reglas o métodos19. El Dockerfile superpone ese código exacto a una base fijada y escribe un marcador; discovery lo contrasta. El marcador no atesta criptográficamente un servidor hostil: el administrador del endpoint aprobado forma parte de la confianza.

## Registro de servidores y fronteras de confianza

ODOO_SERVERS_JSON es configuración del servidor. Una operación de usuario referencia server_ref; no recibe una URL, una base o un método ORM escritos por un LLM. Cada entrada vincula empresa Gestoría, tenant, odoo_company_id, DB, UUID de instancia esperado y referencia de variable con API key. El secreto no se serializa en la conexión pública ni se guarda como credencial en SQLite.

La política de red comprueba esquema, host, ausencia de credenciales/query/fragment en URL y redes autorizadas. El modo HTTP de laboratorio necesita configuración explícita y direcciones privadas/loopback admitidas. La resolución DNS valida todas las IP devueltas, rechaza destinos peligrosos como link-local/metadata y fija una IP de conexión conservando Host y SNI. No se siguen redirects ni proxies heredados del entorno.

El cliente evita convertir el adaptador en un proxy universal. Hay una allowlist cerrada de pares modelo/método. Las escrituras solo pasan por execute_approved del bridge. No se permiten context, allowed_company_ids, sudo, database o base_url enviados como payload de negocio. El contexto de empresa se forma con configuración verificada.

## Identidad, permisos y binding

La autorización valida principal vigente, empresa local, tenant, conexión, estado, configuración y capacidad. GuardedClient vuelve a evaluar el scope antes del cliente; el cliente real tiene un callback antes de cada intento HTTP, incluidos retries de lectura, para que una revocación entre intentos no se ignore. Los jobs reconstruyen al actor desde credenciales/configuración actuales y no caen a owner ante un fallo.

Standalone usa tenant de forma `standalone:<cid>`. El modo integrado exige ODOO_ACTOR_SCOPES_JSON por actor, con tenant_id, companies y capabilities. Un header arbitrario o un OperationEnvelope escrito por un modelo no constituye autorización. Los DTOs no sustituyen la comprobación del servidor.

El binding valida identidad de instancia y compañía remota, versión, usuario no superuser ni settings admin, compañías permitidas y capacidades. Si la identidad fiscal falta o diverge se exige confirmación humana con motivo. No se mapea por nombre, NIF o posición. Reutilizar un binding existente para otra instancia se bloquea; la rotación de credencial no debe alterar la identidad del negocio.

La configuración de escritura está apagada por defecto y necesita IDs permitidos de contactos, diarios, cuentas e impuestos. Multi-company dentro de una DB requiere opción explícita y pruebas; el laboratorio y recomendación inicial usan una base separada por empresa. Una conexión ajena no debe revelar metadatos a otro tenant.

## Discovery y transporte JSON-2

El transporte usa bearer API key y X-Odoo-Database desde el registro aprobado. Las llamadas son POST JSON-2 con parámetros nombrados. Cada llamada Odoo es su propia transacción; no tratar una secuencia create/action_post como una operación atómica. De hecho action_post está prohibido en esta versión.

Se aplican timeout, límites de respuesta, no redirects y errores sanitizados. Las lecturas pueden reintentarse con backoff y un circuit breaker por proveedor; una escritura no se repite ciegamente. Errores de proveedor, autenticación, respuesta inválida, red y timeout se normalizan sin devolver HTML, traceback, DSN o tokens al cliente. Un resultado incierto de escritura se conserva para conciliación.

Discovery consulta el bridge y fields_get para comprobar semántica, no solo un200. Guarda capacidades y evidencia con caducidad de una hora. Modelos o campos faltantes deshabilitan capacidades. Si falta account no se anuncia lectura de facturas como disponible. La salud pública refleja el reporte persistido y su frescura; no debe confundirse con una prueba de conexión en cada GET.

## Lectura, mapeo e importación

Los contactos se leen por páginas ordenadas por id, con límites y scope de compañía por fila. Se probó un fixture de1101 partners sin pérdida/duplicado. Se mantienen IDs externos y no se deduplica por nombre. Los contactos compartidos sin compañía se excluyen deliberadamente del recorrido inicial, en lugar de asumir que pertenecen al tenant.

Las facturas se extraen como snapshots coherentes del bridge. Se consideran out_invoice, in_invoice, out_refund e in_refund; no se suman todas las account.move.line. Se separan líneas comerciales y técnicas, se concilian bases/cuotas/totales y se bloquean moneda o composición no soportadas. La primera correspondencia fiscal es conservadora: un impuesto requiere mapping explícito y comprobación; si no es inequívoco queda other o mapping_blocked.

El flujo es lectura, normalización, staging, preview, aceptación e importación. La aceptación vuelve a comprobar el origen cuando corresponde. Se guardan source hash, IDs, write_date, versión de mapping y advertencias. La importación es transaccional y crea registros unverified, nunca reviewed ni deducibilidad inferida. Lotes iguales no duplican y cambios legítimos no sobrescriben un registro revisado.

Los cursores usan write_date con overlap y lectura por id; solo avanzan tras commit local. El fullscan permite detectar objetos no vistos y abrir conflicto sin borrar historia. El máximo de recorrido y los límites de lote son presupuestos reales, no promesas de capacidad ilimitada. Hay que medir rendimiento y comportamiento frente a cambios concurrentes en la instalación real.

## Jobs, eventos y fallos distribuidos

Los jobs tienen estados persistidos, intentos, disponibilidad, leases y propietario de lease. Se reclaman bajo BEGIN IMMEDIATE, se recuperan leases expiradas y se emiten heartbeats durante previews largos. El ACK final comprueba el propietario, evitando que un worker antiguo confirme el trabajo de otro. Los errores retryable tienen presupuesto; los inciertos o bloqueados no giran indefinidamente.

Outbox/inbox conservan eventos y confirmaciones de consumidor. Los eventos llevan versión, tenant, empresa, correlación y referencias minimizadas; no contienen claves ni documentos completos. La entrega actual es un flujo pendiente por conexión, no un fan-out independiente para cada avatar. El runtime externo distribuye el trabajo después y debe deduplicar por ID.

La reconciliación de escrituras consulta el ledger remoto usando la clave original. Si no aparece confirmación no se inventa éxito ni se ejecuta otro create. Exactly-once HTTP no se promete; buscamos un efecto único mediante identidades persistentes y transacciones del backend.

## Propuestas, aprobaciones y bridge propio

Un dry-run crea una propuesta inmutable con hash, diff, revisión de conexión, autor y caducidad. No modifica registros remotos. Para factura se calcula una cotización pura de impuestos/totales en el bridge, sin crear y deshacer un borrador para simularla. Se bloquean configuraciones no compatibles con el borrador local.

La aprobación requiere principal humano owner/reviewer, hash exacto y revisión. El commit vuelve a validar vigencia del aprobador, propuesta, borrador y capacidad. Una propuesta solo puede tener una ejecución; cambiar idempotency_key no autoriza duplicarla. La firma HMAC remota liga UUID de base, compañía, operation_key, request_hash, aprobación, aprobador y expiración. Así una aprobación de la base A no es válida en B aunque compartan firmante.

`agntia_bridge` aporta identidad de DB, snapshots, adjuntos y ledger. `agntia_bridge_account` añade guardas contables. El marcador interno de escritura es una identidad de objeto Python que JSON no puede fabricar; el bot no accede a CRUD sensible directamente. Se usan una clave única de operación y advisory lock PostgreSQL; creación y ledger deben confirmar o revertir juntos. Su comportamiento concurrente y de aislamiento real todavía debe demostrarse.

La cuenta bot no es administrador. No añadir grupos amplios para hacer pasar una prueba. El addon bloquea publicación y borrado; el backend solo permite contactos y borradores. Adjuntos se limitan, verifican, escanean según configuración y cifran. Riesgos pendientes: instalación ORM/ACL real, addons de terceros que añadan caminos inesperados, restauración, rotación y protección del servidor aprobador. Cualquier fuga de tenant, firma omitida, duplicado, secreto o posible publicación detiene el avance hasta resolver el defecto.


## Fuentes internas para continuar

- [Service y binding](../../../agntia_gestoria/integrations/odoo/service.py).
- [Transporte](../../../agntia_gestoria/integrations/odoo/transport.py).
- [Imports y conflictos](../../../agntia_gestoria/integrations/odoo/imports.py).
- [Propuestas y escrituras](../../../agntia_gestoria/integrations/odoo/commands.py).
- [Bridge remoto](../../../infra/odoo/addons/agntia_bridge/models/bridge.py).

Siguiente lectura: [índice y protocolo de uso](README.md). La evidencia se atribuye al SHA/entorno descrito, no a cualquier checkout posterior.
