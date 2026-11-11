# Pruebas C17

Suite ejecutada localmente: `python -m unittest discover -s tests`, con selector del sandbox limitado a20ms para evitar bloqueo de TestClient. Comando exacto y conteos en [c20/TESTS.md](../c20/TESTS.md) y [local-results.json](../c20/local-results.json). No se afirma que la suite estándar sin workaround haya corrido aquí.

Las pruebas deterministas se encuentran en test_odoo_adapter.py/test_odoo_hardening.py y conservan los tests anteriores. Node: build y archivo odoo.test.mjs ejecutados. La relación con esta fase es su componente descrito en README; no existe una ejecución independiente inventada por campaña.

Gate no local: Instalación ORM/ACL real, dos solicitudes simultáneas y comportamiento de aislamiento/retry PostgreSQL. No afirmar que está instalado. Ejecutar `scripts/odoo_verify.ps1` y completar [pilot-acceptance](../pilot-acceptance.md) con evidencia sanitizada.
