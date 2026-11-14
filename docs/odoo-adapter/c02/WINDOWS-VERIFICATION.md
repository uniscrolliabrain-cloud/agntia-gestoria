# Verificación en Windows

Fecha local de comprobación 2026-11-09. Base `1fd25d932a26acab0d865aa4aa3d7ed83876282e`.
Entorno Windows/PowerShell, Python 3.12.10 y Node 24.18.1.

| Comprobación | Resultado |
| --- | --- |
| `python scripts/verify_baseline.py` | PASS, 43 archivos y 43 rutas inventariadas |
| Build TypeScript, sintaxis de los dos JS del frontend y diff de `typescript/dist` | PASS |
| `python scripts/verify_odoo_source.py --source-root <temporal>` | PASS, 38 comprobaciones estáticas |
| Instalación editable con el extra dev | PASS |
| Suite unittest estándar | PASS, 23 pruebas en 4,398 s |
| Playwright Chromium | PASS, dashboard de escritorio y móvil, alta de registro y descarga PPTX |
| Odoo y JSON-2 reales | BLOCKED |
| Laboratorio C03, dos DB y restauración | NOT VERIFIED |

El primer clon convirtió LF a CRLF. Se configuró `core.autocrlf=false` solo en el clon y se recuperaron los bytes del commit en los archivos cuya única diferencia era esa conversión. Los hashes esperados se conservaron. Para un clon nuevo se puede usar `git clone -c core.autocrlf=false <url>`.

Para la auditoría estática se descargaron en una carpeta temporal los archivos de `odoo/odoo` de las URLs fijadas en `infra/odoo/upstream-lock.json`. El verificador comprobó sus SHA-256 antes de inspeccionar los contratos.

## Bloqueo y criterio de salida

`Get-Command docker` y `docker info --format '{{.OSType}}'` no encontraron el ejecutable. Las rutas estándar de Docker Desktop no contenían los ejecutables y `winget list --id Docker.DockerDesktop --exact --disable-interactivity` no encontró el paquete instalado. WSL indicó versión predeterminada 2 y ninguna distribución instalada.

El laboratorio requiere Docker Desktop con motor Linux local y Compose. Una vez disponible, verificar el contexto, `docker info --format '{{.OSType}}'` y `docker compose version` antes de crear recursos. Queda pendiente decidir con evidencia si se construye desde el SHA auditado o se identifica y reaudita el código de la imagen. La auditoría estática no prueba esa correspondencia, la instalación de módulos, el acceso por bot, el aislamiento ni la restauración.
