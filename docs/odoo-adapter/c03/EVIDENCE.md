# Evidencias C03

Base de implementación remota: `1fd25d932a26acab0d865aa4aa3d7ed83876282e`. El SHA de entrega se consulta en la PR de `feat/odoo-complete-adapter`; no se inventa un SHA por campaña. Se hizo un lote único por instrucción posterior del propietario, no veinte PR ficticias.

Evidencia local compartida: [c20/local-results.json](../c20/local-results.json). Pruebas aisladas/simuladas no son evidencia de ejecución de Docker, ERP ni jurisdicción real.

Artefactos revisables: `infra/odoo/compose.yaml`, `infra/odoo/Dockerfile`, `scripts/odoo_bootstrap.py`, `scripts/odoo_fixture.py`, `scripts/odoo_backup.py`. El diff Git/PR identifica los cambios exactos. No se han publicado logs privados, claves o datos de clientes.

Resultado real pendiente: Construir, arrancar ambas DB, inspeccionar módulos/grupos, backup/restore y conexión cruzada reales.
