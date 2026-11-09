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

Pendiente al crear la rama. La evidencia de GitHub se añadirá cuando termine: instalación dev, suite unittest sin workaround, build Node, comprobaciones JS y navegador original. No se hereda un PASS de ejecuciones históricas.

Se ejecutará también el nuevo verificador de baseline en CI; no se suma como una prueba unittest adicional.
