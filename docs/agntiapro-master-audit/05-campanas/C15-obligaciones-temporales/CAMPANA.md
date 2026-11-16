# C15 — obligaciones-temporales

**Estado:** PLANIFICADA / NO EJECUTADA. **Objetivo:** Versionar calendarios, fuentes, jurisdicción y vigencia. **Justificación:** cerrar una brecha verificable sin reemplazar capacidades consolidadas. **Baseline:** Gestoría main 6b743d1e2c82885298f96a281f097d0bcbf2991a (2026-11-16); antes de ejecutar, Freebuff debe recalcular SHA y comprobar rutas. **Evidencia:** docs/legal-research.md;docs/product-scope.md. La existencia de documentación no demuestra ejecución.

## Arquitectura y alcance
Contrato de entrada: `tenantId`, `companyId`, `actorId`, `correlationId`, `idempotencyKey`, `schemaVersion=1` verificados por servidor; contrato de salida: `status`, `evidenceRefs[]`, `error.code`, `revision`. No aceptar claims arbitrarios como autoridad. Entregable: calendario nominal trazable, sin presentación. Fuera de alcance: presentación tributaria, pagos, facturas publicadas, cambios en agente/main o despliegue. Autoridad: Agente para identidad/policy/approval, Gestoría para expediente/cálculo, Odoo para registros ERP.

## Superficies y árbol de intervención
**Lecturas existentes o históricas a comprobar:** docs/legal-research.md;docs/product-scope.md.
**Candidatos a modificar, comprobar existencia y función antes de editar:** agntia_gestoria/;tests/.
**Archivos NUEVOS propuestos:** `docs/agntiapro-master-audit/05-campanas/C15-obligaciones-temporales/EVIDENCE.md`, `docs/agntiapro-master-audit/05-campanas/C15-obligaciones-temporales/DECISIONS.md` (crear durante ejecución solo si aportan evidencia). **Legacy:** no eliminar sin búsqueda de consumidores y pruebas. **Migración:** aditiva, con backup previo y dry-run; no alterar tablas ni contratos sin ADR y test de rollback.

## Waves y patchsets
### W1 — Descubrimiento y diseño
**PS01.1 / inventario.** PRE: checkout limpio y baseline fijado. LEER: docs/legal-research.md;docs/product-scope.md. OPERAR: inspeccionar rutas reales, callgraph, tests, consumidores y diferencias de ramas archivadas; clasificar REUTILIZAR/REFORZAR/SUSTITUIR. DEP: herramientas ya instaladas; no agregar paquetes. WIRING: registrar productor/consumidor y autoridad. TEST: `python -m pytest -q` (si un comando requiere servicio ausente, marcar BLOCKED). EVIDENCIA: SHA, comandos, salida sanitizada, lista de rutas y gaps. GATE: ninguna ruta asumida sin comprobar. ROLLBACK: revertir solo documentación de esta ola.

**PS01.2 / contrato.** PRE: PS01.1 aprobado. LEER: docs/agente-integration.md y concept master. OPERAR: definir schema versionado, errores tipados, límites, authz, idempotencia, correlación y flags; ADR de alternativas. DEP: reutilizar FastAPI/Pydantic, SDK TS existente; nuevas dependencias solo con licencia/versión y test. WIRING: adaptador de frontera, no importación de archivos privados de Agente. TEST: casos de compatibilidad v1, payload desconocido, actor revocado, tenant cruzado. EVIDENCIA: schema y matriz. GATE: deny-by-default. ROLLBACK: conservar contrato anterior bajo flag.

### W2 — Implementación acotada
**PS02.1 / dominio.** PRE: contrato congelado. LEER: agntia_gestoria/;tests/. OPERAR: implementar versionar calendarios, fuentes, jurisdicción y vigencia reutilizando módulos reales; separar lógica pura, repositorios, adaptadores y rutas; no crear segundo kernel. DEP: pinning y SBOM de cada paquete nuevo. WIRING: API → policy → servicio de dominio → store/adapter → auditoría/outbox. TEST: unitarios con fixtures y negativos, `python -m pytest -q`. EVIDENCIA: diff, casos PASS/FAIL y migraciones. GATE: ninguna operación sensible sin permiso. ROLLBACK: feature flag OFF, conservar operaciones pendientes para reconciliación.

**PS02.2 / fallos.** PRE: PS02.1 PASS. OPERAR: instrumentar timeout, crash antes/después de commit, replay con misma clave y payload distinto, fallo remoto y concurrencia entre tenants. WIRING: estado durable y correlationId propagado. TEST: integración y concurrencia, con dos empresas; servicios no disponibles = NOT VERIFIED, nunca PASS. EVIDENCIA: trazas sin PII ni secretos. GATE: cero cross-tenant y cero efectos duplicados. ROLLBACK: detener nuevas escrituras, reconciliar pendientes sin restauración destructiva.

### W3 — Certificación y handoff
**PS03.1 / E2E y operación.** PRE: W2 verde. OPERAR: ejecutar test E2E con servicios reales cuando proceda, health/readiness, métricas de errores y latencia, restauración y compatibilidad de SDK; actualizar runbook. TEST: `python -m pytest -q`; pruebas live de Odoo solo con Docker disponible. EVIDENCIA: versión/imagen/commit, entorno, tiempos medidos, logs sanitizados. GATE: todos los casos obligatorios PASS o BLOCKED explícito; BLOCKED impide cierre. ROLLBACK: apagar flag y reponer binario previo conservando ledger.

**PS03.2 / reporte.** PRE: PS03.1 evaluado. OPERAR: registrar SHA inicial/final, archivos, tests, bugs, fixes, decisiones, riesgos y PR; entregar handoff a C16. GATE: trazabilidad requisito→patchset→commit→test→evidencia. No merge ni deploy sin fundador.

## Pruebas y gates
Unit: invariantes de dominio y formatos; integración: persistencia y API; E2E: actor→runtime→Gestoría→proveedor si aplica; seguridad: IDOR, cross-tenant, revocación, inyección y secretos; fallos: replay, timeout, restart, 409 distinto payload; rendimiento: medir p50/p95 sin inventar SLO. Health y readiness independientes. **Aceptación:** calendario nominal trazable, sin presentación, evidencia reproducible, política fail-closed, rollback ensayado. **Riesgos:** compatibilidad, legislación vigente, Odoo live y permisos externos. **Decisiones pendientes:** proveedor, alcance fiscal, autoridad de cada campo, umbrales operativos, aprobación del fundador.

## EXECUTION-REPORT — plantilla sin ejecutar
Fecha: PENDIENTE; rama: PENDIENTE; SHA inicial/final: PENDIENTE; patchsets: NO EJECUTADOS; archivos: PENDIENTE; tests PASS/FAIL/SKIP: PENDIENTE; bugs/fixes: PENDIENTE; divergencias: PENDIENTE; dependencias: PENDIENTE; riesgos: PENDIENTE; integración: NO VERIFICADA; handoff: PENDIENTE.
