# CONCEPT MASTER — AGNTIA GESTORÍA

**Versión:** 1.0 · **Fecha:** 2026-11-15 · **Serie:** 03/14 · **Estado:** visión arquitectónica, no certificación de implementación

> Documento rector evolutivo. Preservar las especificaciones y evidencias existentes; las capacidades objetivo no deben presentarse como operativas.

## 1. Propósito y tesis

Agntia Gestoría es el dominio especializado de gestión empresarial, fiscal, contable, documental y laboral de AgntiaPro. No sustituye a la autoridad fiscal, a un profesional habilitado ni a Odoo: coordina datos, propuestas, cálculos acotados, revisiones y evidencias. Laia supervisa; Juan ejecuta el rol de gestoría; Marcos opera tareas administrativas autorizadas. Los nombres de agentes no conceden permisos.

## 2. Baseline comprobado y límites

README y docs/product-scope.md describen FastAPI/Python 3.11+, SQLite y originales en disco, API y SDK TypeScript @agntia/gestoria con Hono; motor 303 y 130 para supuestos estrictos de territorio común 2026; documentos, registros, expedientes, revisiones, informes y auditoría. Odoo Community 19 dispone de código de adaptador, bridge y laboratorio, pero docs/odoo-adapter/pilot-acceptance.md declara NO VERIFICADO el piloto real. No hay presentación tributaria, emisión fiscal acreditada, conciliación bancaria operativa ni automatización laboral integral. La documentación existente contiene estado histórico de ramas; cualquier afirmación de despliegue exige SHA, ejecución y evidencia actuales.

## 3. Principios innegociables

LLM propone, reglas deterministas disponen. Deny-by-default, fail-closed, tenant isolation, least privilege, idempotencia y replay. Una factura borrador no es emitida; un cálculo no es declaración; un expediente aprobado no es presentación; una solicitud enviada no es aceptación. Nunca convertir ausencia de información en exención o conformidad. No inventar legislación ni clasificación de gastos. Nunca exponer token owner, credenciales fiscales o ERP al navegador ni al modelo.

## 4. Arquitectura objetivo

Usuario/LAIA/Juan/Marcos → runtime AgntiaPro (identidad, tenant, políticas, approvals, SOP, event bus) → SDK TS servidor/Hono → API Gestoría FastAPI → motores deterministas, expediente, auditoría y almacenamiento → adaptadores ERP Odoo, bancos/PSD2, documentos, administraciones y RRHH. Odoo autoridad sobre entidades ERP; Gestoría autoridad sobre revisiones fiscales, evidencia y preparación; AgntiaPro autoridad sobre ejecución, conversación y aprobación transversal. El binding tenant→empresa Gestoría→DB/compañía Odoo se valida antes de cada llamada. Sin binding unívoco: BLOCKED.

## 5. Catálogo objetivo de capacidades (72)

01 alta de empresa; 02 perfil fiscal; 03 actividad CNAE/IAE propuesta; 04 territorios; 05 obligaciones propuestas; 06 calendario versionado; 07 avisos; 08 agenda; 09 contactos; 10 clientes; 11 proveedores; 12 ingestión de facturas; 13 ingestión de tickets; 14 OCR revisable; 15 extracción estructurada; 16 deduplicación; 17 provenance; 18 hash originales; 19 versionado documental; 20 retención; 21 registro ingresos; 22 registro gastos; 23 anulación trazable; 24 clasificación propuesta; 25 revisión humana; 26 conciliación importaciones; 27 conciliación bancaria; 28 libros IVA; 29 libros IRPF; 30 borradores contables; 31 validación doble partida; 32 plan contable; 33 inmovilizado; 34 amortizaciones; 35 cierres; 36 cuentas anuales; 37 motor 303; 38 motor 130; 39 motor 390; 40 motor 349; 41 motor 111; 42 motor 115; 43 motor 190; 44 motor 180; 45 motor 131; 46 motor 100; 47 motor 200; 48 motor 202; 49 IGIC; 50 IPSI; 51 forales; 52 versiones normativas; 53 validación oficial; 54 expedientes fiscales; 55 revisión de casillas; 56 autorización representación; 57 presentación autorizada; 58 justificantes; 59 rectificativas; 60 nóminas; 61 convenios; 62 contratos; 63 altas y bajas; 64 cotizaciones; 65 Sistema RED; 66 control de vencimientos; 67 informes y dashboards; 68 alertas explicables; 69 integración Odoo; 70 integración bancaria regulada; 71 exportación de datos; 72 auditoría y reconstrucción. ESTE CATÁLOGO ES OBJETIVO, NO IMPLEMENTACIÓN.

## 6. Modelo de dominio y contratos

Company, TaxProfile, Jurisdiction, Obligation, SourceDocument, EconomicRecord, Review, TaxPreparation, TaxCalculation, TaxFiling, Receipt, ERPBinding, SyncRun, ExternalReference, Approval, AuditEvent y Evidence. Toda entidad incluye tenantId, companyId, schemaVersion, timestamps, actor, source, revision y correlationId donde proceda. Importes Decimal, moneda explícita y período fiscal. Los eventos son append-only, ordenados por secuencia de commit, con idempotencyKey y causationId; no se usan timestamps como orden canónico. Los contratos Zod/JSON Schema/Pydantic se verifican en CI, con migraciones y compatibilidad aditiva.

## 7. Flujos canónicos

F1 documento→antivirus→hash→extracción→validación→propuesta→revisión→registro. F2 Odoo→lectura autorizada→normalización→unverified→revisión→reconciliación. F3 registros revisados→scope fiscal comprobado→motor determinista→casillas+evidencias→aprobación→preparación; presentación solo con conector, representación y justificante oficiales. F4 petición de agente→plan SOP→policy→dry-run→approval vinculada al hash→ejecución idempotente→verificación→auditoría. F5 error/transitorio→retry acotado→DLQ→intervención→replay seguro. F6 cambios en fuente→invalidación de cálculos y preparaciones anteriores.

## 8. Seguridad y gobernanza

Roles separados owner/reviewer/agent/viewer; autorizaciones de servidor por operación y objeto; prohibido proxy ORM libre. Owner/reviewer aprueban, agent propone y consulta solo scopes concedidos. Controles contra prompt injection documental, exfiltración, SSRF, IDOR, cross-tenant, race conditions y replay. Secretos en vault, TLS, cifrado en reposo, logs redactados, rotación/revocación, backups cifrados y restauración ensayada. RGPD: minimización, propósito, base jurídica, derechos, residencia y retención por clase. Fiscalidad y laboral sujetos a revisión de expertos y legislación vigente.

## 9. Odoo Community y sincronización

Instancia autoalojada aislada por tenant según diseño validado; discovery de versión, addons, modelos, ACL y compañía; capacidades unsupported explícitas. Bridge transaccional con ledger, operation_key, HMAC de aprobación y reintentos sin duplicados. Importaciones siempre unverified; escrituras solo contacto sintético y borradores aprobados en piloto. No action_post, facturación real, asientos, pagos, correos o impuestos hasta gates específicos. Backups incluyen PostgreSQL+filestore y SQLite+originales. La fuente autoritativa se documenta por campo.

## 10. Plan por etapas y gates

P0 inventario de código, SHA y pruebas reproducibles. P1 identidad/tenancy/policy y catálogo de herramientas. P2 piloto Odoo real con dos DB sintéticas, ACL, variante sin account, bridge, concurrency, crash/recovery, restore. P3 ingestión, documentos y registro económico revisado. P4 303/130 reforzados con golden cases y normativa versionada. P5 contabilidad, conciliación y bancos mediante proveedores autorizados. P6 fiscalidad adicional por modelo/territorio, uno a uno. P7 RRHH/laboral con permisos y fuentes oficiales. P8 integración AgntiaPro, UX, observabilidad y piloto humano. Ninguna fase se declara PASS con tests skipped; evidencias incluyen comando, SHA, entorno, fixture, resultado, logs sanitizados y responsable.

## 11. Roadmap de campañas ejecutables

C01 baseline y manifest; C02 matriz de capacidades reales; C03 threat model; C04 contratos de tenant; C05 políticas por herramienta; C06 SDK TS/Hono; C07 Odoo live environment; C08 ACL y bindings; C09 importadores idempotentes; C10 ledger/bridge; C11 pruebas de concurrencia; C12 evidencia documental; C13 revisión y stale invalidation; C14 golden tests 303; C15 golden tests 130; C16 calendarios normativos; C17 contabilidad y reconciliación; C18 adapter banking read-only; C19 event bus y observabilidad; C20 backup/restore; C21 UX de expedientes; C22 aprobaciones runtime; C23 piloto multitenant; C24 auditoría final y go/no-go. Cada campaña debe documentar archivos exactos, precondiciones, patchset, tests, riesgos, rollback y reporte; los archivos concretos se determinan tras inventario, nunca por suposición.

## 12. Integración de agentes y UX

Laia presenta situación, riesgos, tareas y decisiones. Juan gestiona documentos, propuestas y cálculos permitidos; Marcos organiza entradas y seguimiento. Los humanos conservan las decisiones sensibles. Chat muestra estados verdaderos: recibido, analizando, verificando, esperando aprobación, ejecutando, completado/bloqueado; nunca progreso fingido ni temporizadores inventados. Centro de Control expone trace, correlationId, evidencia, stale, retries y actor. Workspaces Gestoría, Documentos, Tareas y Control Center comparten IDs y permisos.

## 13. Métricas y criterios de éxito

Exactitud de cálculos dentro de scope 100% frente a golden cases; cero accesos cross-tenant; cero duplicados ante replay; 100% escrituras sensibles auditadas; restauración verificada; ratio de documentos con evidencia; tiempo de revisión; tasa de stale detectado; errores por adaptador; coste por expediente. Umbrales de latencia, RTO/RPO y throughput se fijan después de medir la infraestructura real, no se inventan.

## 14. Definición de terminado y siguientes decisiones

Concept aprobado no equivale a producto terminado. Una capability está DONE solo con código, test automatizado, pruebas de integración reales cuando proceda, seguridad, observabilidad, documentación, rollback y aprobación. No integrar en producción ni fusionar ramas sin consentimiento del propietario. Próxima acción: inventario completo por SHA y mapa de archivos; después campañas secuenciales y revisión de reports por Freebuff/Codex.

## Referencias internas

- README.md
- docs/product-scope.md
- docs/calculation-engines.md
- docs/agente-integration.md
- docs/odoo-adapter/pilot-acceptance.md
- ODOO-IMPLEMENTATION-HANDOFF.md
- VISION-Y-PLAN-AGNTIA-GESTORIA.md

## Control de cambios

V1.0: marco conceptual transversal, 72 capacidades objetivo, arquitectura, invariantes, 24 campañas propuestas y gates. Requiere posterior inventario exhaustivo de código y validación de runtime real.
