# Evidencias C01

- Baseline remoto: `ae8db06bf548fa7c190a2ee5e5acf52075e343ba`.
- Árbol verificado local/remoto: `572b06b1ea2bec2307d94136eb742bc5dcb61081`.
- `baseline-inventory.json`: 43 archivos originales y 43 rutas API; SHA-256 por archivo.
- `local-results/results.json`: comandos, códigos de salida y tiempos de esta ejecución.
- `local-results/*.log`: salida capturada de procesos de prueba sintéticos. No contienen secretos, documentos de clientes ni configuración real de Odoo.
- PR: https://github.com/uniscrolliabrain-cloud/agntia-gestoria/pull/1, abierta y no fusionada.
- Revisión ejecutada: `f95a945449994deea8313d1c501c055522ea8dff`.
- CI existente: https://github.com/uniscrolliabrain-cloud/agntia-gestoria/actions/runs/42653348715 — success, 23 tests sin workaround y navegador desktop/mobile aprobado.
- Verificador: https://github.com/uniscrolliabrain-cloud/agntia-gestoria/actions/runs/42653348825 — success, 43 archivos originales.
- `ci-evidence.json`: resultado y tiempos de los pasos obtenidos de GitHub. La actualización documental posterior debe mantener checks verdes antes de fusionar.

El código de producción no cambia. La comparación con el snapshot ausente queda NOT VERIFIED. No hay conexión Odoo, ningún contenedor iniciado ni operaciones remotas de negocio en esta fase.
