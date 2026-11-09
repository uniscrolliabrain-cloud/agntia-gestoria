# C01 · Congelación y reproducibilidad

Objetivo: documentar el código real antes de incorporar Odoo, con una referencia remota comprobada y sin cambios en producción.

## Archivos y contratos

- `../00-baseline.md`: SHA, comparación local/remoto y limitación del volcado ausente.
- `baseline-inventory.json`: hashes de los 43 archivos existentes, 43 rutas, firmas Python y exports TypeScript.
- `../../../scripts/verify_baseline.py`: verificador independiente de FastAPI, bases de datos, red y credenciales.
- `local-runner.py`, `local-results/`: comandos efectivamente ejecutados, tiempos, códigos y logs.
- `EVIDENCE.md`, `TESTS.md`, `RISKS.md`, `DECISIONS.md`: evidencia, comprobaciones y decisiones.
- Workflow aditivo `odoo-baseline.yml`: comprobación del inventario en CI. La CI existente conserva las pruebas estándar y navegador.

No se añaden endpoints ni se modifica ningún archivo de producción, tests originales, fórmula fiscal o migración. Los permisos Odoo continúan inexistentes; ninguna capacidad remota queda habilitada por esta PR.

## Reproducir

```sh
python scripts/verify_baseline.py
pip install -e '.[dev]'
python -m unittest discover -s tests -v
node typescript/scripts/build.mjs
node --check agntia_gestoria/static/app.js
node --check agntia_gestoria/static/dashboard.js
python -m playwright install chromium
python scripts/browser_check.py
```

Para reproducir los diagnósticos específicos del sandbox Linux, crea `.venv` con acceso a dependencias del entorno y ejecuta `python docs/odoo-adapter/c01/local-runner.py`. Sobrescribe únicamente sus logs locales; revisa el diff antes de subir evidencia nueva. El workaround de selector está confinado al proceso de pruebas, nunca al código del servicio ni a CI.

Siguiente paso: cerrar el gate de baseline, obtener revisión y permiso de fusión de esta PR, y comenzar C02 fijando el upstream Odoo 19.0. No confundir esa aprobación con permiso para modificar `agente` o desplegar producción.
