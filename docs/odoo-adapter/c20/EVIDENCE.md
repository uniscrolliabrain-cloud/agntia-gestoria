# Evidencias C20

Base de implementación remota: `1fd25d932a26acab0d865aa4aa3d7ed83876282e`. El SHA de entrega se consulta en la PR de `feat/odoo-complete-adapter`; no se inventa un SHA por campaña. Se hizo un lote único por instrucción posterior del propietario, no veinte PR ficticias.

Evidencia local compartida: [c20/local-results.json](../c20/local-results.json). Pruebas aisladas/simuladas no son evidencia de ejecución de Docker, ERP ni jurisdicción real.

Artefactos revisables: `tests/test_odoo_adapter.py`, `tests/test_odoo_hardening.py`, `tests/integration/test_odoo_live.py`, `.github/workflows/odoo-lab.yml`. El diff Git/PR identifica los cambios exactos. No se han publicado logs privados, claves o datos de clientes.

Resultado real pendiente: Ejecutar Docker/live/fallos/concurrencia/restauración/UI y aceptación; rendimiento/coste real aún no medidos.
