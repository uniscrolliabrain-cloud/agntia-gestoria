# Pruebas C01

Ejecutadas localmente el 09/11/2026; logs en `local-results/`. No hay pruebas Odoo en esta fase.

| Comprobación | Exit | Tiempo (s) | Lectura del resultado |
| --- | --- | --- | --- |
| install-dev-offline | 1 | 0.615 | BLOCKED: pytest no disponible offline |
| install-runtime-offline | 0 | 1.006 | PASS |
| unit-standard | 124 | 15.02 | BLOCKED local: timeout 15 s; no es una suite completada |
| unit-selector-workaround | 0 | 10.222 | PASS: 23 ejecutados, 23 aprobados, 0 fallidos; ajuste test-only |
| node-build | 0 | 0.082 | PASS |
| node-app-syntax | 0 | 0.027 | PASS |
| node-dashboard-syntax | 0 | 0.024 | PASS |
| node-dist-unchanged | 0 | 0.003 | PASS |
| python-compile | 0 | 0.034 | PASS |
| baseline-inventory | 0 | 0.084 | PASS |
| browser-local | 1 | 0.1 | BLOCKED: bind de socket denegado antes de lanzar navegador |
| docker-local-socket | 1 | 0.048 | BLOCKED: acceso al socket Docker denegado |

Python local: 3.12.14. Node local: 24.22.1. Entorno Linux, UID 1000.

## Dependencias observadas

- pytest: no instalado
- fastapi: 0.141.1
- starlette: 1.6.0
- pydantic: 2.13.4
- httpx: 0.28.1
- uvicorn: 0.52.1
- python-multipart: 0.0.32
- python-dotenv: 1.2.2
- python-pptx: 1.0.2
- reportlab: 4.4.9
- playwright: 1.62.0
- setuptools: 84.2.1

## CI de esta PR

PASS observado en el commit `f95a945449994deea8313d1c501c055522ea8dff` de esta PR: [CI](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/actions/runs/42653348715) y [verificador de baseline](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/actions/runs/42653348825). Instalación dev, suite unittest **sin workaround**, build Node, comprobaciones JS y navegador original aprobaron. El log de CI indica `Ran 23 tests in 1.088s`, seguido de `OK`, y `Desktop/mobile dashboard, report download and record creation passed`. Los pasos y tiempos están en `ci-evidence.json`. Esta evidencia corresponde a esa revisión; el commit que agrega este texto se verifica de nuevo mediante los mismos workflows.

También se ejecutó el nuevo verificador de baseline en CI; no se suma como una prueba unittest adicional.
