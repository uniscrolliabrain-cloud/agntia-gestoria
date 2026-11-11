# Runbook Windows / servidor · laboratorio sintético

No se han ejecutado estos pasos Docker en el entorno implementador. Requisitos: Docker Desktop Linux containers o Docker Engine + Compose v2, daemon/context local verificado, Git, Python 3.12, Node 24; 6–8 GB RAM recomendados como hipótesis inicial, no medición.

## PowerShell

```powershell
git clone https://github.com/uniscrolliabrain-cloud/agntia-gestoria.git
Set-Location agntia-gestoria
git fetch origin
git switch feat/odoo-complete-adapter
$Lab = Join-Path $env:LOCALAPPDATA 'AgntiaGestoriaSyntheticLab'
.\scripts\odoo_verify.ps1 -StateDir $Lab -Provision -StartApp
```

El script crea venv, instala dev, ejecuta tests locales/SDK, prepara estado privado fuera del repo, construye Odoo fijado, aprovisiona dos DB sintéticas, ejecuta smoke y E2E. Si ya hay estado, no lo resetea automáticamente. Un bootstrap interrumpido requiere inspección privada antes de continuar: los fixtures rechazan reprovisionar el bot para no rotar claves o duplicar datos inadvertidamente. La política de ejecución PowerShell se gestiona por el propietario; alternativamente ejecutar los comandos Python equivalentes, sin cambiar una política global desde el agente.

La API opcional queda en http://127.0.0.1:8010 y Odoo interno en loopback8069; PostgreSQL no expone puerto. Nunca pegar tokens en capturas o chat. El fichero run-env.json contiene secretos. Restringir carpeta con permisos NTFS del propietario. Los comandos usan solo DB agntia_test_a/b; el reset exige su flag explícito y destruye únicamente volúmenes del proyecto sintético nombrado.

## Linux o comandos equivalentes

```bash
python -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m unittest discover -s tests -v
node typescript/scripts/build.mjs
node --test typescript/tests/odoo.test.mjs
python scripts/odoo_bootstrap.py --state-dir /tmp/agntia-private-lab --synthetic-lab --prepare
python scripts/odoo_bootstrap.py --state-dir /tmp/agntia-private-lab --synthetic-lab --bootstrap
python scripts/odoo_smoke.py --state-dir /tmp/agntia-private-lab
AGNTIA_RUN_ODOO_TESTS=1 AGNTIA_LAB_STATE_DIR=/tmp/agntia-private-lab python -m unittest discover -s tests/integration -v -f
```

Usar el Python del venv para los últimos comandos también (o activarlo). `scripts/odoo_run_local.py --state-dir RUTA` levanta API host; añadir --worker en otra terminal para procesar jobs. `--start-app` del bootstrap ejecuta API+worker en contenedores en lugar de host. No usar dos APIs contra datos compartidos sin control de despliegue.

## Incidencias

- Source/instance mismatch: detener; verificar imagen y DB. No modificar expected_instance_id para ocultar una mezcla entre empresas.
- 424/stale: revalidar conexión por humano autorizado y confirmar ámbito. No usar credenciales admin como fallback.
- reconciliation_required: conservar clave original y ejecutar `odoo_reconcile.py`; si no hay ledger remoto, investigar. El script no repite create.
- Conflicto: preservar original, revisar documentos, elegir keep_local o supersede_local con motivo. Nunca unlink remoto.
- Error de arranque/addon/ACL: guardar logs privados localmente y redactar secretos antes de reportar. Corregir contra el SHA fijado y volver a probar aislamiento/borrador antes de seguir.

Backup: `python scripts/odoo_backup.py --state-dir RUTA --database agntia_test_a --backup`. Restore: mismo script con `--restore-from RUTA_BACKUP --confirm-synthetic-restore`. Cada ensayo usa una base nueva `agntia_test_restore_<id>` y valida el adjunto por ORM. El reset sintético elimina esas copias junto con el resto del laboratorio. Registrar hashes y conteos observados.
