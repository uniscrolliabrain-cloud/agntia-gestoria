# Arquitectura implementada

`AgntiaPro → @agntia/gestoria (servidor Hono) → FastAPI → Adapter → JSON-2 → Odoo Community 19`.

El cliente solo consume capacidades de negocio nominadas. La identidad viene de las credenciales verificadas de Gestoría; el modo integrado añade la configuración de ámbitos por actor. Ningún nombre de avatar concede permisos. El repositorio `agente` no se modifica.

## Componentes y autoridad

- Gestoría custodia hechos fiscales declarados, clasificación, revisión, cálculos acotados y evidencias locales.
- Odoo custodia contactos, configuración contable y movimientos. Se conservan snapshots de origen, enlaces y hashes.
- `Service/GuardedClient` comprueba actor vigente, empresa, tenant, conexión, binding, configuración y capacidad antes de cada HTTP, también desde jobs.
- `Imports` separa lectura, staging, aceptación e importación. Una importación nunca aprueba un registro. Cambios remotos generan conflictos y marcadores de invalidación; no sobrescriben una revisión.
- `Jobs` usa BEGIN IMMEDIATE, leases, heartbeats, presupuesto de reintentos y claves persistentes. No se promete exactly-once HTTP.
- `Commands` separa dry-run, aprobación humana, commit y conciliación. El ledger remoto hace efectiva la idempotencia dentro de la transacción Odoo.
- `Attachments` conserva originales cifrados con hash y descarga explícita; scanner requerido por defecto. Los documentos no se envían al LLM.

## Addons propios

`agntia_bridge` depende de base, contacts y rpc. Proporciona identidad de DB, discovery, snapshots/adjuntos y operaciones cerradas. `agntia_bridge_account` añade ACL y guardas contables al instalar account. No se copia upstream; licencia LGPL-3. Sin bridge la conexión falla cerrada: no hay fallback a ORM genérico.

La imagen base está fijada por digest y se superpone el código Odoo del SHA auditado. Discovery comprueba el marcador de ese SHA además de versión, identidad DB, permisos y campos. El marcador no es una atestación criptográfica del sistema remoto: se confía en el administrador del servidor aprobado.

## Persistencia y límites

La migración aditiva tiene backup previo y transacción. Los secretos viven fuera de SQLite. Tablas de conexiones, enlaces, staging, jobs, cursores, outbox/inbox, propuestas, aprobaciones, conflictos e idempotencia conservan el vínculo de empresa. SQLite sigue siendo el backend inicial; no usar réplicas distribuidas ni NFS como si fuera PostgreSQL.

No se implementa scheduler de Laia, banca, presentación fiscal, facturación electrónica, nóminas o VERI*FACTU. No hay interfaz Odoo visible nueva ni integración aplicada en AgntiaPro. La API y SDK permiten la conexión posterior.
