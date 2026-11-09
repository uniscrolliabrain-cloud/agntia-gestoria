# Informe al founder · estado de la campaña Odoo

Fecha de actualización: 2026-11-09. Informe parcial de la primera fase; no acredita que el adaptador esté terminado o instalado.

| Campaña | Estado | Evidencia / siguiente condición |
| --- | --- | --- |
| C01 Baseline | PASS (baseline remoto; snapshot ausente NOT VERIFIED) | PR [#1](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/pull/1), revisión `f95a945449994deea8313d1c501c055522ea8dff`; CI y navegador PASS. Pendiente aprobación de fusión. |
| C02 Upstream | BLOCKED | Espera cierre y revisión/fusión autorizada de C01. No hay SHA o imagen Odoo fijados todavía. |
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

Permitido en esta entrega: inventariar, verificar, documentar, publicar rama y PR de C01 y ejecutar su CI. Ninguna operación Odoo habilitada. No se llama action_post, no se contabilizan asientos, no se envían impuestos, correos o pagos; no hay scheduler empresarial paralelo.

No se modifica `agente`, upstream Odoo, producción, secretos ni fórmulas fiscales. La rama principal no se actualiza con la campaña hasta aprobación de fusión.

## Decisión del propietario

Revisar la PR concreta de C01 cuando finalice su CI y autorizar su fusión para seguir la secuencia. No se solicita permiso para producción ni para `agente`. Antes de C03 hará falta un laboratorio Docker accesible y aislado o una alternativa autorizada, con evidencia de dos DB y bots separados. Antes del piloto: gates completos y aceptación expresa.
