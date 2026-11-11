# Modelo de amenazas y riesgos residuales

Fronteras: navegador/chat no confiable; SDK servidor con principal acotado; API Gestoría; SQLite/documentos locales; transporte privado; bot Odoo por DB; addon/ERP bajo administrador de confianza. Los originales y texto remoto son datos no confiables, nunca instrucciones para elevar capacidades.

| Amenaza | Control implementado | Verificación restante |
|---|---|---|
| Mezcla tenant/compañía/DB | binding explícito, UUID DB, company/context, revalidación cada HTTP y job | Dos DB y credenciales intercambiadas reales |
| SSRF/DNS rebinding/metadata | registro servidor, CIDR, rechazo de link-local/redirect/URL credentials, IP fijada y SNI | TLS/DNS reales en servidor |
| Escritura por bot fuera de política | allowlist de negocio, HMAC ligado a DB, marker Python privado y guardas ORM | ACL/transacción reales Odoo, módulos adicionales |
| Repetición/timeout/concurrencia | claves persistentes, reserva local, ledger remoto único, advisory lock, lectura de conciliación | PostgreSQL aislamiento/retries/concurrencia real |
| Publicación o pago | no herramienta ni método en allowlist; guardas _post y estado draft | Intentos negativos de caminos indirectos instalados |
| Impuesto inferido erróneo | mapeo aprobado, reconciliación, campos unresolved, unverified, revisión humana | Fixtures fiscales representativos y revisión competente |
| Archivos maliciosos | límites/MIME/hash/scan por defecto, cifrado, no LLM automático | Scanner operativo, política DLP/retención |
| Secretos en logs/UI | referencias, errores sanitizados, centinelas en tests | Auditoría operativa de reverse proxy/host/backups |
| Auditoría alterada | cadena hashes + comprobación outbox | Administrador DB puede reescribir todo; falta anclaje externo |

Limitaciones explícitas: SQLite no distribuido; bot y firmante residen en el mismo servidor Gestoría si no se separa un approval service; compromiso de ese servidor rompe esa frontera. La etiqueta owner/reviewer procede de la configuración autenticada, no prueba por sí sola intervención física humana. Proteger sus credenciales con SSO/MFA en el gateway antes de producción. Las aprobaciones no incorporan verificación biométrica ni certificación fiscal.

No se implementa protección general de todos los flujos del ERP: el bot debe tener SOLO el grupo restringido configurado; addons de terceros pueden añadir métodos públicos y ACL. Revisar grupos efectivos y reglas tras cada actualización. El bridge protege sus modelos usados; no prometer cobertura de un árbol Odoo/OCA no auditado.

El selector de base/list_db se desactiva y los puertos del laboratorio se ligan a loopback; esto no configura firewall/TLS de producción. Docker usa secretos locales de prueba y PostgreSQL privilegiado únicamente para provisión sintética. Nunca reutilizar ese rol como rol de producción.

Condiciones de parada: fuga de ámbito, posible publicación, pérdida de auditoría, duplicación remota, firma omitida, secreto expuesto o ambigüedad fiscal sin bloqueo. Resolver antes de piloto; conservar pruebas sanitizadas y no ocultar fallos cambiando mocks.
