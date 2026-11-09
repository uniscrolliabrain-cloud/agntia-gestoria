# Informe al founder · estado de la campaña Odoo

Fecha de actualización: 2026-11-09. Informe parcial de C01 y auditoría estática C02; no acredita que el adaptador esté terminado o instalado.

| Campaña | Estado | Evidencia / siguiente condición |
| --- | --- | --- |
| C01 Baseline | PASS (baseline remoto; snapshot ausente NOT VERIFIED) | PR [#1](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/pull/1), revisión `f95a945449994deea8313d1c501c055522ea8dff`; CI y navegador PASS. Fusionada con aprobación del propietario en `0626ae218983337163c569bb9dc589e98775088a`. |
| C02 Upstream | BLOCKED | SHA, digests y matriz fijados; 38 comprobaciones estáticas PASS. Gate integral BLOCKED: instancia, permisos y contratos reales NOT VERIFIED; PR [#2](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/pull/2) fusionada para el handoff por orden explicita del propietario, sin cerrar el gate runtime; fuente y CI PASS en `09cc1cdb3994f6c978b5d0f777161d0717da8137`, sin integración real. |
| C03 Laboratorio | NOT VERIFIED | Socket Docker local denegado; no se ha arrancado Odoo ni dos bases de test. |
| C04 Contratos | NOT VERIFIED | No iniciado; depende de las fases anteriores. |
| C05 Migraciones | NOT VERIFIED | No iniciado; SQLite y datos originales intactos. |
| C06 Conexiones/secretos | NOT VERIFIED | No iniciado; no se han configurado credenciales. |
| C07 Transporte JSON-2 | NOT VERIFIED | No iniciado; no hay HTTP de negocio a Odoo. |
| C08 Discovery | NOT VERIFIED | No iniciado; capacidades de instancia desconocidas, ninguna habilitada. |
| C09 Binding/tenancy | NOT VERIFIED | No iniciado; falta laboratorio de aislamiento. |
| C10 Contactos | NOT VERIFIED | No iniciado. |
| C11 Facturas | NOT VERIFIED | No iniciado; no hay mapeo fiscal implícito. |
| C12 Staging/import | NOT VERIFIED | No iniciado. |
| C13 Sync/reconciliación | NOT VERIFIED | No iniciado. |
| C14 Adjuntos | NOT VERIFIED | No iniciado. |
| C15 Write-back contactos | NOT VERIFIED | No iniciado; escritura remota deshabilitada. |
| C16 Borradores Odoo | NOT VERIFIED | No iniciado; no se publica ni crea ninguna factura Odoo. |
| C17 Bridge opcional | NOT VERIFIED | Necesidad no evaluada; no se crea un addon de relleno. |
| C18 API/TS/Hono Odoo | NOT VERIFIED | No iniciado; API y exports originales conservados. |
| C19 Agentes/SOP/eventos | NOT VERIFIED | No iniciado; repositorio `agente` sin modificar. |
| C20 Hardening/E2E/entrega | NOT VERIFIED | No iniciado; A–E no ejecutados. |

## Resultados observados

23 tests aprobados localmente con workaround explícito del selector del sandbox; 0 fallidos en esa ejecución. Suite estándar local: timeout, no suite aprobada. Instalación dev offline: bloqueada por pytest ausente. Instalación runtime y build/sintaxis Node: PASS. Navegador local: bloqueado por sockets. CI estándar de esta PR: [PASS](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/actions/runs/42653348715), 23 ejecutados, 23 aprobados, 0 fallidos, sin workaround; navegador desktop/mobile y descarga de presentación aprobados. Verificador de baseline: [PASS](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/actions/runs/42653348825). Evidencia observada en `f95a945449994deea8313d1c501c055522ea8dff`; el último estado de la PR debe comprobarse antes de la fusión.

No hay tests Odoo ejecutados, ni métricas de latencia/coste por tenant medidas, ni bases de datos de clientes utilizadas. Coste incremental Odoo en esta fase: no desplegado; no equivale a coste operativo cero del producto. Las hipótesis de infraestructura se fijarán tras C02/C03.

## Operaciones y permisos

C01 fusionada por autorización explícita del propietario. Permitido en C02: auditar fuentes públicas, fijar referencias, documentar, publicar PR borrador y verificar fuentes/CI. Ninguna operación Odoo habilitada. No se llama action_post, no se contabilizan asientos, no se envían impuestos, correos o pagos; no hay scheduler empresarial paralelo.

No se modifica `agente`, upstream Odoo, producción, secretos ni fórmulas fiscales. C01 y la auditoria parcial C02 estan en main. El propietario autorizo expresamente guardar todo en main para el relevo al laptop; C02 se fusiono en `1f8b7542d859ede4ea8b624fd3a4371ea603190e`. Esa instruccion no aprueba el gate runtime, futuras fusiones o produccion.

## Decisión del propietario

C01 fue aprobada con «Fusionala» y ya está fusionada. El propietario ordeno posteriormente incorporar el avance y un handoff detallado a main para continuar en su laptop. Se ejecuto esa instruccion de conservacion; C02 sigue requiriendo resolver los gates tecnicos de instalacion real. El acceso Docker quedó sin ejecutar y el entorno sufrió indisponibilidad temporal. Hacen falta un laboratorio aislado accesible y una correspondencia de imagen/código verificada. C03–C20 no se consideran aprobadas por la auditoría estática. Antes del piloto: gates completos y aceptación expresa.

## Relevo Windows

Leer [HANDOFF-CODEX-WINDOWS.md](../../HANDOFF-CODEX-WINDOWS.md) en la raiz: estado, autorizaciones, PowerShell, mapa tecnico, contratos, pruebas, C03–C20 y prompt para el siguiente Codex. Los comandos Windows son una receta de continuacion, no evidencia de ejecucion en el laptop.
