param(
    [Parameter(Mandatory=$true)][string]$StateDir,
    [switch]$Provision,
    [switch]$StartApp
)
$ErrorActionPreference = 'Stop'
function Assert-NativeSuccess { param([string]$Step) if ($LASTEXITCODE -ne 0) { throw "$Step fallo con exit $LASTEXITCODE" } }
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot
$Py = Join-Path $RepoRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $Py)) { py -3.12 -m venv .venv; Assert-NativeSuccess 'venv' }
& $Py -m pip install -e '.[dev]'; Assert-NativeSuccess 'install'
& $Py -m unittest discover -s tests -v; Assert-NativeSuccess 'unit tests'
node typescript/scripts/build.mjs; Assert-NativeSuccess 'SDK build'
node --test typescript/tests/odoo.test.mjs; Assert-NativeSuccess 'SDK contracts'
if ($Provision) {
    if (-not (Test-Path (Join-Path $StateDir 'AGNTIA_SYNTHETIC_LAB.json'))) {
        & $Py scripts/odoo_bootstrap.py --state-dir $StateDir --synthetic-lab --prepare
        Assert-NativeSuccess 'private synthetic state'
    }
    if (-not (Test-Path (Join-Path $StateDir 'run-env.json'))) {
        & $Py scripts/odoo_bootstrap.py --state-dir $StateDir --synthetic-lab --bootstrap
        Assert-NativeSuccess 'Odoo fixtures'
    }
}
& $Py scripts/odoo_smoke.py --state-dir $StateDir
Assert-NativeSuccess 'real provider smoke'
$env:AGNTIA_RUN_ODOO_TESTS = '1'
$env:AGNTIA_LAB_STATE_DIR = (Resolve-Path $StateDir).Path
try {
    & $Py -m unittest discover -s tests/integration -v -f
    Assert-NativeSuccess 'real Odoo E2E'
} finally { Remove-Item Env:AGNTIA_RUN_ODOO_TESTS -ErrorAction SilentlyContinue }
if ($StartApp) {
    & $Py scripts/odoo_bootstrap.py --state-dir $StateDir --synthetic-lab --start-app
    Assert-NativeSuccess 'container API and worker'
}
Write-Host 'Tests executed. Preserve sanitized results only; never upload private state or credentials.'
