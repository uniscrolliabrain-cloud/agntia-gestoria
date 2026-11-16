# Contrato de transición Agente ↔ Gestoría

## Baselines
Gestoría main `6b743d1e2c82885298f96a281f097d0bcbf2991a`; Agente main observado en historial `54b8d5407a8576459448c4d059a877297d18ca7a` (no garantiza HEAD actual). Rama V2 `audit/preflight-cognition-option3-20261115` accesible. Inspeccionado `apps/server/src/engine/sop-executor.ts` en V2: usa Zod, SOP tipado, EventBus y tareas; no acoplar Gestoría a este archivo interno. Las campañas C00–C15 de harness V2 son propuestas hasta verificación por archivo y SHA.

## Adaptador recomendado
Agente: autenticación humana → tenant y rol canónicos → policy/SOP → approval de acción sensible → service-to-service client con credencial de corto alcance y contexto firmado/atestado → Gestoría: validación de credencial, audiencia, issuer, expiración, tenant, actor, company binding y scope de capacidad → lógica dominio → evento/outbox. No aceptar `tenantId`, `actorId` ni `approvalRef` únicamente por estar en JSON.

Compatibilidad con auth legacy: feature flag para tokens por empresa de Gestoría solo en entorno controlado. No delegar token owner; no permitir que un agente simule owner/reviewer. No reemplazar `authenticate` hasta contar con pruebas de sesiones y regresión.

## Matriz de tests obligatoria
CT-01 lectura actor tenant A/company A PASS.
CT-02 actor tenant A/company B 404/403, sin efecto.
CT-03 actor agent no puede approve/commit/cerrar expediente.
CT-04 token revocado o expirado DENY.
CT-05 misma idempotencyKey+payload → mismo job; distinto payload → 409.
CT-06 timeout tras commit → reconcile sin duplicado.
CT-07 error SDK top-level vs detail conserva código.
CT-08 readOnlyTools contiene 0 elementos mutates=true.
CT-09 event sequence y cursor de tenant cruzado rechazados.
CT-10 servicio caído: estado blocked, no éxito inventado.
CT-11 contract version incompatible: error explícito.
CT-12 no segundo kernel ni autorización por prompts.
