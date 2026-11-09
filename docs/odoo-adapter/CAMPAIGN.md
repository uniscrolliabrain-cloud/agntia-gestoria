# Contrato de ejecución · campaña Odoo Community × AgntiaPro

Origen: campaña maestra 1.0 facilitada por el propietario el 09/11/2026. Este documento resume los límites de ejecución; no sustituye las especificaciones detalladas del propietario ni acredita fases no realizadas.

Implementación primaria: `uniscrolliabrain-cloud/agntia-gestoria`. Upstream de referencia: `odoo/odoo`, rama 19.0. Integración posterior: `uniscrolliabrain-cloud/agente`, únicamente con aprobación expresa independiente.

## Secuencia autorizada

Una rama `feat/odoo-cNN-slug` y PR autocontenida por campaña, con README, EVIDENCE, TESTS, RISKS y decisiones. Ejecutar pruebas y documentar resultados reales. No avanzar si falla el gate. Revisar y fusionar secuencialmente; no se presupone permiso para fusionar o desplegar. La PR concreta y sus resultados se presentan al propietario antes de pedir esa aprobación.

Orden: C01 baseline; C02 upstream fijado y matriz; C03 laboratorio de dos DB; C04 contratos; C05 migraciones; C06 registro y secretos; C07 transporte JSON-2; C08 discovery; C09 bindings/aislamiento; C10 partners; C11 facturas; C12 staging/importación; C13 sync y reconciliación; C14 evidencias; C15 write-back de contactos; C16 borradores; C17 bridge solo si hace falta; C18 API/TS/Hono; C19 herramientas/SOP/eventos; C20 hardening y E2E A–E.

## Invariantes

- Odoo autogestionado Community, invisible como backend del producto; no Enterprise ni promesas fiscales universales.
- Preservar motores fiscales, territorio, revisión humana, evidencias y API existente. Los cambios a archivos protegidos de la campaña necesitan justificación, no-regresión y la revisión explícita indicada por el propietario.
- No tocar `agente`, upstream, producción ni secretos sin aprobación expresa. No crear un scheduler empresarial paralelo al runtime de AgntiaPro.
- Identidad y tenant autenticados; bindings explícitos UUID Gestoría ↔ conexión ↔ DB ↔ compañía entera Odoo. Fallar cerrado y comprobar antes de HTTP.
- Configuración remota solo del servidor; sin URL, base de datos, dominio ORM o método arbitrario suministrado por agente. Secretos por referencia, nunca en SQLite/exportaciones/logs.
- Importar como unverified, sin inferir IVA/IGIC o deducibilidad; documentos no confiables, nunca permisos o instrucciones de sistema.
- Escritura solo de contactos y borradores, tras dry-run y aprobación ligada al mismo hash. Idempotencia persistente y reconciliación de resultados inciertos; sin retry ciego tras timeout de escritura.
- Prohibidos action_post, eliminación de movimientos/justificantes, contabilización automática, correos, pagos, transferencias y presentación de impuestos.
- Cada fase conserva actor, empresa, correlación, origen y evidencia. No simular aprobaciones ni actividad de Laia o los demás agentes.
- Si no se dispone del entorno real, marcar sus pruebas NOT VERIFIED. Mocks no equivalen a Odoo real. No usar datos de clientes.

## Stop conditions

Fuga cross-tenant, posible publicación de factura, error fiscal, ambigüedad de impuesto/territorio, bypass de aprobación, pérdida de auditoría, duplicación tras timeout o secreto expuesto: detener la fase hasta resolverlo. No maquillar resultados ni aumentar permisos como fallback.

Estado, PRs, métricas y decisiones del propietario: [final-report.md](final-report.md). C01 no instala un adaptador.
