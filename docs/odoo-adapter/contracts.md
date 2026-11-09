# Contratos y API Odoo v1

DTOs Python: `agntia_gestoria/integrations/contracts.py`; SDK: `typescript/odoo.ts`, declaraciones en `typescript/types/odoo.d.ts`. Modelos Pydantic rechazan campos extra y valores no finitos. Money se transmite como string decimal; no se infiere deducibilidad. Los tokens de write_date remotos conservan el formato UTC Odoo para comparación exacta.

Prefijo: `/api/companies/{cid}/integrations/odoo`. IDs locales son hex32. Ningún body contiene URL, DB, credencial, dominio ORM o allowed_company_ids suministrado por agentes.

| Método | Sufijo | Efecto |
|---|---|---|
| POST | connections / connections/validate / connections/disable | Owner/reviewer, configuración por server_ref aprobado, revisión optimista |
| GET | health / capabilities | Estado persistido, caducidad y capacidades; no hace ping en cada petición |
| POST | imports/preview | 202, job con resource partners/invoices, full e idempotency_key |
| POST | imports | 202, job con staging_ids e idempotency_key |
| GET | jobs/{id}, staging, conflicts | Solo ámbito del principal; staging puede contener PII autorizada |
| POST | conflicts/{id}/resolve | Humano, revision, decision keep_local/supersede_local, notes |
| GET | invoice-drafts/{id}/projection-input | Hash del borrador local para propuesta |
| POST | partners/dry-run, invoice-drafts/dry-run | Propuesta inmutable y diff; ninguna escritura remota |
| POST | proposals/{id}/approve | Humano, revision, proposal_hash y notes |
| POST | partners/commit, invoice-drafts/commit | proposal_id, approval_id, expected_revision, idempotency_key |
| POST | writes/reconcile | Consulta ledger por clave original, nunca repite create |
| GET/POST | invoices/{remoteId}/attachments[/download] | Metadatos / descarga explícita cifrada |
| POST | records/{id}/classification | Clasificación humana, evidencia y fecha; vuelve a unverified |
| GET | audit-integrity, metrics, events, briefing | Evidencias y estado real |
| POST | events/ack | Confirmación de event_ids por consumidor autenticado |

GET events entrega hasta 500 pendientes para el consumidor de eventos del tenant. ACK es persistente e idempotente; esta versión usa un único flujo de entrega por conexión, no fan-out independiente para todos los avatares. El runtime distribuye después las referencias.

Los imports son dos trabajos: pedir preview, ejecutar worker/pollear job, examinar staging_ids; pedir import, ejecutar worker/pollear job. No bloquear Hono esperando un lote. Cada job vuelve a verificar permisos y revisión del binding.

Errores uniformes: `{code,message,correlation_id,retryable,reconciliation_required}`. La ruta preserva semánticas HTTP de auth/forbidden/not_found/conflict/validation/dependency/upstream/timeout; los mensajes remotos y tracebacks se descartan. Una escritura incierta devuelve un resultado de negocio reconciliation_required aunque el transporte HTTP a Gestoría haya respondido 200.

Una aprobación dura como máximo la caducidad de la propuesta (15 min). La prueba HMAC remota dura como máximo 5 min al emitirla y vincula instance_id, company, operación, hash y aprobador. Se vuelve a comprobar que el aprobador no esté revocado. Una propuesta tiene una única ejecución: cambiar la clave no permite volver a crear.

Capacidades desconocidas o caducadas bloquean HTTP de negocio. No se certifica cumplimiento por importar l10n_es. Canarias/forales/Ceuta/Melilla mantienen sus bloqueos existentes; esta integración no amplía motores territoriales.
