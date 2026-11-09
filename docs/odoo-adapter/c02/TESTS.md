# Pruebas C02

Ejecutado localmente:

- `python scripts/verify_odoo_source.py --source-root /workspace/scratch/odoo-c02 --output docs/odoo-adapter/c02/static-checks.json`: PASS, 38 comprobaciones de fuente. Incluye hashes exactos de los 16 archivos del core inspeccionados, handler JSON-2, campos/tipos, reglas relevantes y licencias declaradas.
- El verificador no importa Odoo, no consulta DB y no es un test de integración.
- `python scripts/verify_baseline.py`: se vuelve a ejecutar antes de publicar para comprobar que los 43 archivos originales no han cambiado.

Los 23 tests de servicio y el navegador de la CI existente aprobaron en la revisión `09cc1cdb3994f6c978b5d0f777161d0717da8137`: [ejecución](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/actions/runs/42676011890). También aprobó el workflow de [contratos estáticos](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/actions/runs/42676012171). Es evidencia nueva de C02, no un resultado heredado de C01. La actualización documental posterior se vuelve a comprobar mediante los mismos workflows.

NOT VERIFIED: instalación Odoo limpia, módulos con/sin account/l10n_es, credenciales bot, errores reales JSON/HTML, read/write y rollback, dos DB, backups/restore, concurrencia y E2E A–E. No hay pruebas contra datos reales.
