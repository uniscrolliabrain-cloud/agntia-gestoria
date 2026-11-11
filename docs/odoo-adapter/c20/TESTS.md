# Pruebas de entrega C20

Conteos y versiones reales en [local-results.json](local-results.json). Se ejecutan los 23 tests originales y los tests nuevos de adaptador/hardening; no hay cliente real en esta suite.

Comando local del sandbox:

```python
import selectors, unittest
original = selectors.DefaultSelector.select
selectors.DefaultSelector.select = lambda self, timeout=None: original(self, min(.02, timeout) if timeout is not None else .02)
r = unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.discover('tests'))
raise SystemExit(not r.wasSuccessful())
```

Este ajuste solo pertenece al proceso de prueba local; no altera código de producción ni CI. CI ejecuta unittest estándar sin este ajuste. Node reportó un archivo de prueba aprobado (contiene cuatro escenarios declarados); no contabilizamos cuatro resultados independientes inexistentes en su salida. Build SDK, compileall, sintaxis JS y política exacta del baseline comprobados localmente.

Las pruebas live solo se descubren con `python -m unittest discover -s tests/integration -v -f`, requieren opt-in y marker privado. No fueron ejecutadas aquí. E2E A usa PDF y clasificación sintéticos; no acredita emisión fiscal real. D usa un snapshot de cálculo de prueba; se debe ampliar a revisión/cálculo completo en el piloto. E simula pérdida del ACK local después de una operación real y concilia por ledger; el timeout real de red y la carrera concurrente remota aún deben ensayarse.

La ejecución manual Docker tiene pasos de backup/restore, no resultados aprobados. Navegador de revisiones anteriores no acredita navegador de este commit. Registrar PASS/FAIL/NOT VERIFIED sin heredar aprobaciones.


## Confirmación remota posterior

CI sobre código84504053d71c966db58d8de0fdf44b9817ebef82: 57 tests Python aprobados sin workaround (7.079s), cuatro escenarios Node aprobados, instalación dev y navegador desktop/móvil/descarga/creación PASS. Fuente y baseline PASS. Ver [ci-results.json](ci-results.json), con URLs verificadas. Esta evidencia supersede solo los pendientes de CI/navegador de la evidencia local; Docker/Odoo real siguen NOT VERIFIED. Instalación editable runtime en .venv y ayuda del entrypoint worker también comprobadas; la instalación global se rechazó por home de solo lectura, sin cambiar permisos.
