# Handoff actual · módulo Odoo · 2026-11-09

Este documento sustituye el estado «C03–C20 no iniciadas» de HANDOFF-CODEX-WINDOWS.md. Conserva sus antecedentes, pero el código del adaptador, addons, SDK y laboratorio ya está implementado en la rama `feat/odoo-complete-adapter`. El propietario pidió completar todo el código y delegó Docker/pruebas reales a la IA del laptop.

Ruta del checkout del implementador: `/workspace/Agntia-gestoria`. Remoto: https://github.com/uniscrolliabrain-cloud/agntia-gestoria. Base main `1fd25d932a26acab0d865aa4aa3d7ed83876282e`. No se conoce ni se inventa la ruta local Windows del propietario. Clonar donde prefiera, hacer fetch y switch de la rama. No se ha tocado `agente`.

## Leer en este orden

1. docs/odoo-adapter/final-report.md — estados por fase y evidencia real.
2. docs/odoo-adapter/c20/local-results.json — conteos/versiones locales.
3. docs/odoo-adapter/RUNBOOK.md — PowerShell y Docker sintético.
4. docs/odoo-adapter/pilot-acceptance.md — gates no ejecutados.
5. docs/odoo-adapter/architecture.md, contracts.md, operations.md, threat-model.md — fronteras e invariantes.
6. docs/odoo-adapter/agent-integration.md — instalación Hono/pnpm y wiring propuesto, sin aplicarlo.
7. docs/odoo-adapter/c03…c20/ — objetivo, pruebas, evidencia, decisiones y riesgos de cada fase.

## Arranque en PowerShell

```powershell
Set-Location RUTA_REAL_DEL_CLON
git fetch origin
git switch feat/odoo-complete-adapter
$Lab = Join-Path $env:LOCALAPPDATA 'AgntiaGestoriaSyntheticLab'
.\scripts\odoo_verify.ps1 -StateDir $Lab -Provision -StartApp
```

Los comandos son una receta, no evidencia de ejecución. Requieren daemon local Docker/Compose2, Python3.12 y Node24. La carpeta de estado privado debe quedar FUERA del repo. No publicar run-env.json, fixtures.private.json, claves, dumps o logs privados. El script no resetea datos existentes automáticamente. Proteger permisos NTFS. Ver Runbook para recuperación si el bootstrap queda a medias.

## Qué hay implementado

Integrations/contracts+errors+migrations+registry+policy; Odoo transport/discovery/service/reads/mappers/imports/jobs/commands/attachments/vault/evidence/routes; addons agntia_bridge y agntia_bridge_account; SDK Odoo y tools; allowlist Hono; pruebas unitarias, live opt-in, workflow manual, backup/restore y smoke/reconcile. Se consolidan nombres propuestos en módulos cohesivos; no faltan archivos de relleno por no replicar cada nombre del plan.

El bridge es necesario: aporta UUID de DB, snapshot coherente, transacción+ledger y HMAC de aprobación que la API create genérica no garantiza. La fuente Odoo exacta se superpone a la base fijada y discovery comprueba su marcador. Sin addons/marker o permisos suficientes, se bloquea la capacidad; no hay fallback admin.

Los motores fiscales, territorios, fuentes legales, tax.py y storage.py originales permanecen idénticos a baseline. Ocho fuentes originales cambian con hashes exactos y ADR; el verificador rechaza más cambios y no permite eximir motores/storage. Importaciones unverified sin deducibilidad inferida; clasificar/revisar exige humano y documentos. Una factura ERP draft no prueba emisión.

## Trabajo de validación restante

Construir/instalar realmente Odoo19+Postgres, corregir cualquier incompatibilidad de ORM/ACL frente al SHA fijado y ejecutar smoke/live A–E. D usa un snapshot sintético de cálculo: ampliar a revisión/cálculo real completo después de mutación remota. E simula ACK local perdido: añadir timeout de red y doble solicitud concurrente real, sin cambiar a otro operation_key. Ejecutar variante sin account/sin permisos, rotación/revocación, recuperación WAL y PostgreSQL+filestore, scanner y navegador. El formulario checklist conserva estos pendientes explícitos.

La suite local usa un ajuste del selector del sandbox para TestClient; en laptop/CI ejecutar unittest estándar primero. No copiar ese workaround a producción. Las pruebas reales están fuera de discovery normal y requieren AGNTIA_RUN_ODOO_TESTS=1 más marker privado. No dar PASS a un skip.

## Límites para la siguiente IA

No publicar facturas ni asientos, no llamar action_post, no enviar correos, pagos ni impuestos. No borrar historial ni movimientos para resolver replays. No ampliar deducibilidad por LLM. Ante mezcla tenant/DB, firma omitida, publicación posible, secreto, pérdida de auditoría o duplicado: parar, resolver y volver a probar. No tocar repo agente o producción sin aprobación. No interpretar nombre de avatar como privilegio. No afirmar cumplimiento fiscal universal.

Entrega código y evidencias por PR; no fusionar automáticamente por el hecho de ejecutar este handoff. Mantener el feature flag off en producción. Toda limitación se reporta con FAIL/BLOCKED/NOT VERIFIED, nunca se maquilla como terminada.


## Código publicado y CI verificada

PR https://github.com/uniscrolliabrain-cloud/agntia-gestoria/pull/4; SHA de código `84504053d71c966db58d8de0fdf44b9817ebef82`. CI estándar confirma57/57 Python sin workaround,4/4 Node y navegador desktop/móvil, descarga y creación de registro. Ver docs/odoo-adapter/c20/ci-results.json. Docker/contratos reales Odoo siguen pendientes; no confundir navegador de la UI existente con pruebas de ERP.


## Visión de producto acordada · 2026-11-10

Leer [VISION-Y-PLAN-AGNTIA-GESTORIA.md](VISION-Y-PLAN-AGNTIA-GESTORIA.md) para la especificación detallada: middleware sobre Odoo Community autoalojado, experiencia AgntiaPro, matriz de capacidades, recorridos, VERI*FACTU, fiscalidad, bancos, contabilidad, operaciones, laboral y fases P0–P8. Es una hoja de ruta; no modifica las guardas ni acredita funciones todavía no integradas.


## Paquete de relevo del 10 de noviembre

[docs/handoff/2026-11-10/README.md](docs/handoff/2026-11-10/README.md) reúne seis documentos de más de mil palabras cada uno: historia del chat, base Python/fiscalidad, adaptador Odoo, API/agentes, pruebas/operación y futuro del producto. Incluye manifiesto de conteos y hashes, evidencia histórica y pendientes explícitos.
