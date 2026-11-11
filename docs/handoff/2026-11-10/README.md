# Handoff para otras IAs · 10 de noviembre de2026

Este paquete conserva el contexto del chat, el estado técnico y el futuro del proyecto. Contiene seis documentos principales, cada uno de al menos1000 palabras, más este índice y un manifiesto de conteos/hashes. No es una transcripción literal: organiza las decisiones disponibles y marca sus fuentes, límites y pendientes. Las preguntas que no figuran en el historial no se reconstruyen a partir de respuestas aisladas.

## Orden de lectura

| Parte | Documento | Contenido |
|---|---|---|
| 01 | [Historia, decisiones y visión](01-historia-decisiones-y-vision.md) | Agntia-video, nacimiento de Gestoría, campaña, correcciones, demo y autorizaciones |
| 02 | [Base Python y fiscalidad](02-base-python-datos-fiscalidad-y-reportes.md) | Datos, SQLite, actores, expedientes, motores, documentos, auditoría y reportes |
| 03 | [Adaptador Odoo](03-adaptador-odoo-sincronizacion-y-seguridad.md) | Registro, aislamiento, HTTP, discovery, importación, jobs, conflictos, firmas y addons |
| 04 | [API, TypeScript y agentes](04-api-typescript-agentes-y-experiencia.md) | SDK/Hono, contratos, UI, herramientas, aprobaciones, eventos y runtime futuro |
| 05 | [Pruebas y operación](05-pruebas-docker-windows-y-operaciones.md) | Evidencia real, Windows, Docker, fixtures, backups, recuperación y piloto |
| 06 | [Futuro y entrega](06-futuro-verifactu-capacidades-y-plan-de-entrega.md) | Holded/Community, VERI*FACTU, bancos, contabilidad, fiscalidad, operaciones y laboral |

## Estado que debe verificar la IA receptora

El repositorio principal es `uniscrolliabrain-cloud/agntia-gestoria`; el checkout del implementador está en `/workspace/Agntia-gestoria`. La ruta del laptop Windows no se conoce. La rama de entrega es `feat/odoo-complete-adapter`, PR[#4](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/pull/4), abierta al empezar este paquete. Su head era e69bd7facfd54ef37539e34dbac130527bd098e2. El código del adaptador y su evidencia CI se referencian por separado en los documentos.

No asumir que main contiene la PR. No modificar `agente`, producción, secretos o las guardas de emisión por leer una hoja de ruta. El propietario pidió autonomía para implementar el adaptador y delegó Docker a la IA del PC; no pidió inventar los resultados de esa ejecución. Nuevas emisiones, pagos o presentaciones necesitan el alcance y la aceptación correspondientes.

## Protocolo de relevo

1. Leer git status, rama y SHA; conservar cambios ajenos.
2. Leer las seis partes y el [plan de producto](../../../VISION-Y-PLAN-AGNTIA-GESTORIA.md).
3. Comprobar [evidencia CI](../../odoo-adapter/c20/ci-results.json) y [gates pendientes](../../odoo-adapter/pilot-acceptance.md).
4. Continuar el laboratorio sintético con el [Runbook](../../odoo-adapter/RUNBOOK.md); no contratar cloud para una demo que el usuario quiere en su PC.
5. Registrar resultados reales con SHA, comandos y entorno. No llamar PASS a un skip o prueba escrita sin ejecución.
6. Entregar cambios pequeños y recuperables; usar las capacidades existentes del ERP y los controles del middleware.

[manifest.json](manifest.json) contiene los conteos y SHA256 de los seis documentos. Los hashes detectan cambios respecto a esta edición, no son una firma de identidad ni una atestación de producción. Los resultados históricos de tests no se vuelven a ejecutar por añadir documentación: se verifica estructura, enlaces, longitud y baseline; las suites técnicas se repiten cuando cambie su alcance o implementación.
