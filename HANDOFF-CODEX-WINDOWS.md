# HANDOFF MAESTRO PARA CODEX EN WINDOWS / POWERSHELL

**Proyecto:** Agntia Gestoría × Odoo Community × futura AgntiaPro  
**Propietario GitHub:** `uniscrolliabrain-cloud`  
**Repositorio de trabajo:** <https://github.com/uniscrolliabrain-cloud/agntia-gestoria>  
**Fecha del traspaso:** 2026-11-09  
**Destinatario:** Codex en el laptop del propietario, con acceso a PowerShell y a sus herramientas locales.  
**Estado de esta entrega:** código existente, C01 y auditoría estática C02 guardados en `main`. El adaptador funcional Odoo todavía NO está implementado.  
**Idioma de coordinación:** español. Si hace falta preguntar al propietario, una pregunta cada vez; continuar mientras tanto con trabajo independiente autorizado.

Este documento es el punto de entrada del relevo. Está pensado para que el siguiente agente no necesite reconstruir la conversación, repetir decisiones ya tomadas, inventar resultados o confundir un blueprint con código ejecutable. Es largo intencionadamente: contiene situación, permisos, evidencia, arquitectura, comandos, contratos, decisiones, riesgos y criterios de aceptación.

La fuente de verdad del código es el checkout actual de GitHub, no la memoria de ningún agente. Leer este documento completo y los archivos que referencia antes de editar. Leer también los AGENTS.md y políticas que existan en el laptop y sus directorios padre; en la copia de este proyecto utilizada aquí no se encontró un AGENTS.md propio.

---

## 1. Resumen ejecutivo que debes poder repetir sin exagerar

El propietario quiere una gestoría digital completa para pymes y autónomos españoles, manejable por humanos y agentes desde su producto AgntiaPro. Se decidió aprovechar Odoo Community autogestionado como backend ERP invisible, conservando en Gestoría el dominio fiscal acotado, revisión humana, evidencias, permisos y API. Odoo no será la interfaz comercial del cliente y Enterprise no forma parte de este proyecto.

Existe un servicio Python instalable, FastAPI, SQLite, documentos locales, dashboard estático, informes PDF/PPTX/HTML/SVG y cliente TypeScript/Hono. Hay motores 303 y 130 para supuestos muy delimitados del ejercicio 2026, no una gestoría fiscal universal. La renta anual completa, liquidaciones forales, IGIC/IPSI, nóminas y presentación oficial no están implementadas.

La campaña Odoo tiene veinte fases C01–C20. C01 está ejecutada y fusionada. C02 tiene auditoría de código, referencias fijadas y 38 comprobaciones estáticas aprobadas; NO tiene pruebas de instalación/API real, de modo que su gate integral sigue BLOCKED. C03–C20 no están ejecutadas.

La PR #2, que contenía la auditoría parcial de C02, se ha incorporado a `main` por instrucción expresa del propietario para guardar todo antes del relevo. Esa fusión es una decisión de conservación del avance y **no convierte un gate técnico pendiente en PASS**. No borres ni suavices esa distinción en informes posteriores.

Tu primera tarea útil es recuperar un baseline limpio en el laptop, comprobar Docker Desktop Linux y construir un laboratorio aislado reproducible que permita cerrar las verificaciones reales pendientes de C02/C03. No empieces por crear endpoints ORM genéricos, copiar un ERP, modificar fórmulas o integrar `agente`.

---

## 2. Autorización vigente y límites de alcance

### 2.1 Instrucciones efectivas del propietario

1. Construir el producto de gestoría sobre `agntia-gestoria` sin rehacerlo desde cero.
2. Aplicar la campaña maestra Odoo de manera incremental, con pruebas reales, evidencia y límites de confianza.
3. C01: el propietario respondió **«Fusionala»**; la PR #1 fue fusionada.
4. En este relevo solicitó: **«Dame un handoff ultra largo en un doc en el repo pusheado todo a main y le paso la batuta a codex en mi laptop q tiene acceso a mi powershell»**.
5. Esa última instrucción autoriza incorporar el avance existente y este handoff a `main`, incluso la auditoría parcial de C02, documentando sus bloqueos. No autoriza producción ni convierte pruebas pendientes en ejecutadas.

### 2.2 Puedes continuar sin volver a pedir permiso para cada paso rutinario

- Leer este repositorio, su historial, documentación pública y upstream fijado.
- Crear ramas y PRs de las campañas dentro de Gestoría.
- Escribir código del adaptador dentro del alcance, fixtures sintéticos, pruebas y documentación.
- Ejecutar comprobaciones y levantar un laboratorio local de desarrollo aislado cuando las políticas del laptop y el propietario lo permitan.
- Resolver implementación, fallos y conflictos ordinarios de forma reversible, sin perder trabajo ajeno.
- Proponer en documentos cómo conectarse más adelante con AgntiaPro.

### 2.3 No tienes autorización general para

- Modificar `uniscrolliabrain-cloud/agente`; necesita aprobación expresa independiente.
- Cambiar upstream Odoo ni servicios productivos del propietario.
- Instalar Enterprise o incorporar módulos de terceros indiscriminadamente.
- Crear secretos reales, rotar credenciales productivas o publicar credenciales en el repo/chat/logs.
- Ejecutar facturación definitiva, `action_post`, asientos oficiales, pagos, conciliaciones bancarias, nóminas, transferencias o declaraciones fiscales.
- Aprobar en nombre de un humano porque un agente tenga nombre de persona o rol narrativo.
- Fusionar automáticamente todas las futuras PRs: se conserva la disciplina de revisión y fusión por fase, salvo una instrucción posterior explícita del propietario.
- Borrar volúmenes Docker o datos sin comprobar que pertenecen únicamente al laboratorio sintético y que la acción está autorizada.
- Cambiar globalmente la política de ejecución de PowerShell, TLS, antivirus, firewall o permisos de sistema para hacer pasar pruebas.

La autorización de este handoff no debe reutilizarse como una aprobación futura de C03–C20. Si pides aprobación, primero entrega una PR concreta revisable con pruebas y riesgos. Explica brevemente de qué instrucción sale la necesidad; no repitas permisos ya concedidos para el mismo acto.

---

## 3. Historial, SHAs, ramas y PRs que debes cotejar

| Hito | Referencia |
| --- | --- |
| Baseline público previo a Odoo | `ae8db06bf548fa7c190a2ee5e5acf52075e343ba` |
| Árbol exacto del baseline original | `572b06b1ea2bec2307d94136eb742bc5dcb61081` |
| PR C01 | <https://github.com/uniscrolliabrain-cloud/agntia-gestoria/pull/1> |
| Fusión C01 | `0626ae218983337163c569bb9dc589e98775088a` |
| Rama C01 histórica | `feat/odoo-c01-baseline` |
| Revisión C01 con evidencia inicial | `f95a945449994deea8313d1c501c055522ea8dff` |
| Último head C01 antes de fusionar | `8178680ec83c6dfe65cb850c69cdc96f37591f8c` |
| PR C02 | <https://github.com/uniscrolliabrain-cloud/agntia-gestoria/pull/2> |
| Rama C02 | `feat/odoo-c02-upstream-audit` |
| Revisión C02 con evidencia de CI inicial | `09cc1cdb3994f6c978b5d0f777161d0717da8137` |
| Último head C02 antes del relevo | `df989bef743c6b7a17777c57a86644f61108c97b` |
| Fusión de C02 para guardar el relevo | `1f8b7542d859ede4ea8b624fd3a4371ea603190e` |

El commit que contiene este documento será posterior a la fusión anterior. Obtén su SHA real con `git rev-parse HEAD` o GitHub; no esperes que un archivo pueda contener de antemano el hash del mismo commit que lo añade.

### 3.1 Por qué el historial local de la sesión anterior tenía otros SHA

Las primeras publicaciones se hicieron mediante la API Git de GitHub, no mediante un `git push` del historial local. La copia de trabajo tenía commits locales como `bcb3dda`, `73a89a4`, `795a20a`, pero sus árboles coincidían con los árboles remotos correspondientes. Se comprobó igualdad de contenido, modos y rutas; nunca se afirmó igualdad de historiales.

Se intentó reconstruir un objeto commit remoto desde metadatos públicos y no se reprodujo el hash canónico. No se movieron referencias hacia objetos no verificados. No repitas ese rodeo: en el laptop, usa un clon/fetch normal con Git y conserva el historial remoto verdadero.

### 3.2 Volcado `agntia-gestoria.txt`

La campaña del propietario mencionaba un snapshot de 2.813 líneas y aproximadamente 205 KB. Ese archivo no estaba adjunto ni disponible en el entorno utilizado. No se cotejó byte a byte. Los archivos del baseline real sumaron 43 archivos, 2.625 líneas y 210.759 bytes, con un método de recuento diferente que incluye artefactos JS compilados. No deduzcas identidad ni diferencias semánticas solo de esas cantidades.

Si el propietario facilita el volcado en el laptop, regístralo como fuente adicional y compara; no detengas la recuperación del código remoto por no tenerlo. No afirmes haber auditado un adjunto ausente.

---

## 4. Estado real por campaña

| Fase | Estado al entregar | Qué existe | Qué falta para cerrar |
| --- | --- | --- | --- |
| C01 | PASS respecto del baseline remoto | Inventario, firmas, hashes, logs, CI, documentación y verificador | Comparación con el volcado ausente sigue NOT VERIFIED |
| C02 | BLOCKED en gate integral; auditoría estática PASS | Pin de código/docs/imagen, fuentes, matriz, licencias, 38 checks y CI | Instalación real, permisos bot, métodos/errores y relación imagen/código |
| C03 | NOT VERIFIED | Solo requisitos y referencias de infraestructura | Laboratorio reproducible de dos DB, bots, salud, backup/restore y aislamiento |
| C04 | NOT VERIFIED | Contratos propuestos por la campaña/documento | DTOs implementados y tests de serialización/validación |
| C05 | NOT VERIFIED | SQLite original intacto | Migraciones aditivas, índices y recuperación/concurrencia |
| C06 | NOT VERIFIED | Diseño de conexiones propuesto | Registro seguro, secretos por referencia y políticas |
| C07 | NOT VERIFIED | Contrato JSON-2 leído | Transporte robusto real, mocks y prueba Odoo |
| C08 | NOT VERIFIED | Matriz estática, ninguna capacidad habilitada | Discovery persistido de instancia y fail-closed |
| C09 | NOT VERIFIED | Requisitos de binding definidos | Aislamiento efectivo tenant/DB/compañía |
| C10 | NOT VERIFIED | Modelo partner inspeccionado | Lectura/importación paginada de contactos |
| C11 | NOT VERIFIED | Campos contables inspeccionados | Mapeo correcto, totales reconciliados y bloqueos |
| C12 | NOT VERIFIED | Flujo de staging diseñado | Implementación idempotente con procedencia |
| C13 | NOT VERIFIED | Estrategia descrita | Cursores, leases, retries, inbox/outbox y reconciliación |
| C14 | NOT VERIFIED | Control documental existente genérico | Integración de adjuntos Odoo y verificaciones de binarios |
| C15 | NOT VERIFIED | Prohibiciones/política descritas | Write-back de contactos con autorización e idempotencia |
| C16 | NOT VERIFIED | `invoice_draft` local | Creación remota de draft transaccional y comparativa de totales |
| C17 | NOT VERIFIED / opcional | Ningún addon bridge | Decidir con evidencia si hace falta; implementarlo solo entonces |
| C18 | NOT VERIFIED | SDK y Hono genéricos actuales | API/DTO/SDK Odoo nominados y allowlist exacta |
| C19 | NOT VERIFIED | Herramientas genéricas de Gestoría | Tools Odoo, contratos de eventos y guía SOP/rota |
| C20 | NOT VERIFIED | Tests originales y verificadores estáticos | E2E A–E, fallos, hardening, operaciones y piloto |

**No hay adaptador Odoo operativo instalado.** No hay `agntia_gestoria/integrations/odoo` funcional, Compose de laboratorio, bots, sincronización, approvals remotos o bridge. No crees esos nombres como archivos vacíos para poder decir que existen.

La fusión de una PR de documentación no sustituye el gate de la fase que documenta. Conserva dos estados si hace falta: `source_audit=PASS`, `runtime_gate=BLOCKED`.

---

## 5. Producto y contexto de AgntiaPro

El propietario define AgntiaPro como una empresa sintética como servicio. El owner dirige mediante conversación, interfaz y aprobaciones. Laia supervisa; Juan se ocupa del dominio de gestoría; Antonio, finanzas; Marco ejecuta SOPs. Ana y Pedro son RR. HH. y ciberseguridad, fuera del alcance de escritura de este adaptador salvo eventos informativos autorizados.

Los avatares Anam son la capa de presencia. Las políticas y SOPs deterministas ejecutan el trabajo. ERP, banca y CRM son backends invisibles. Un tenant puede representar una empresa con varios humanos y empleados sintéticos.

Todo lo anterior es intención de producto comunicada por el propietario, no evidencia de implementación en este repo ni en `agente`. No digas que Laia ya tiene una rota funcionando, que un avatar ha aprobado algo o que AgntiaPro ya gobierna todos los permisos si no lo has verificado en el repositorio autorizado.

### 5.1 Experiencia deseada

El cliente abre AgntiaPro, pregunta por su empresa, revisa datos e informes, recibe propuestas, aprueba lo que corresponda y ve evidencia. No necesita entrar en Odoo. Las pantallas Odoo pueden existir para administración interna; no deben convertirse en la UX comercial por comodidad técnica.

### 5.2 Trabajo real, no actividad fingida

Cada intervención futura deberá tener principal autenticado, empresa, capacidad, dueño, estado, coste observado o hipótesis declarada, fuentes y resultado. No inventar reuniones, revisiones, llamadas, sincronizaciones o briefs para aparentar cadencia profesional. Si no hubo datos nuevos ni acciones, la comunicación debe decirlo.

---

## 6. Qué está implementado en Gestoría y qué preservar

### 6.1 Servicio y persistencia

- `agntia_gestoria/app.py`: factoría `create_app(data_dir=None)`, rutas existentes, middleware de origen, autenticación y montaje de frontend.
- `cli.py`: `agntia-gestoria`, host local por defecto, puerto 8010, un worker.
- `storage.py`: SQLite con WAL, foreign keys, transacciones `BEGIN IMMEDIATE` y tablas `companies`, `objects`, `audit`.
- `objects` guarda objetos JSON por empresa/tipo, con algunas claves únicas por empresa.
- Documentos originales se guardan en disco dentro de `GESTORIA_DATA_DIR`.

No hay Postgres del servicio, almacenamiento distribuido, cola de tareas productiva ni escalado multiworker demostrado. Odoo sí necesitará PostgreSQL propio; no confundas esa base con la persistencia de Gestoría.

### 6.2 Identidad actual

`auth.py` tiene `Actor(id, role, companies)`. Roles: owner, reviewer, agent, viewer. Las credenciales se configuran por entorno; no hay todavía principal AgntiaPro firmado con tenant/capacidad. En modo sin credenciales se permite únicamente acceso local, pensado para desarrollo.

- owner crea empresas.
- owner/reviewer revisan expedientes y registros fiscales.
- agent puede preparar datos y calcular dentro de permisos, pero no revisar sus registros.
- El nombre narrativo de un agente no modifica el rol autenticado.

No extiendas el fallback local-owner a errores remotos ni conviertas un fallo Odoo en autenticación de administrador.

### 6.3 Casos y revisión humana

El flujo de expedientes es `draft → in_review → reviewed → done`. Ediciones posteriores invalidan la revisión. Se usan revisiones y hashes de contenido para evitar aprobar una versión y cerrar otra.

`done` y `internal_complete` son estados internos. No significan impuesto presentado, pago hecho o asiento contabilizado. Odoo no puede fabricar la aprobación humana ni convertir su propio estado en la aprobación local.

### 6.4 Registros económicos y fiscales

`tax.py` define `TaxRecord`: fecha, clase, descripción, importes, impuesto, contraparte, categoría, tratamiento, tipos, deducibilidad, documentos y notas.

- Los registros nuevos/importados son `unverified`.
- La revisión exige documentos y owner/reviewer.
- Los registros se corrigen anulando internamente y creando una referencia nueva; conservar historia.
- La anulación local no se propagará como `unlink` a Odoo.
- El identificador externo único actual responde 409 al duplicado; no basta para reconciliación de proveedor.
- Hay vista previa CSV y lote de importación atómico de hasta 2.000 filas; CSV máximo 5 MB.
- La fecha económica registrada no demuestra por sí sola el devengo fiscal adecuado.

### 6.5 Motores fiscales

`engines.py` mantiene reglas deterministas acotadas `aeat-common-2026-v1`:

- 303: trimestres 1T–4T de 2026, tributación común exclusiva AEAT, régimen general interior, tipos 4/10/21 y cuotas corrientes de gastos íntegramente deducibles. Casos excluidos bloquean. Algunos gastos sin IVA explícitamente clasificados se identifican fuera de casillas.
- 130: directa normal no agraria, supuestos ordinarios, acumulados desde enero, previos y minoración según hechos declarados; excluye simplificada/módulos y varias particularidades.
- Requieren registros revisados, soportados y de clase admitida.
- Los resultados contienen fórmulas, casillas, fuentes, versión y huella.
- No hay presentación oficial ni cumplimiento universal.

No modificar estas fórmulas como parte de un mapeador ERP. Odoo suministra hechos y evidencia; no transforma automáticamente su factura en un TaxRecord elegible. Conservar `category=other`, `vat_treatment=other`, tipos/deducibilidad sin resolver cuando no exista prueba suficiente.

### 6.6 Borradores y reportes

- `invoice_draft`: borrador económico, sin número fiscal emitido; `draft_not_issued`.
- `journal_draft`: equilibrio debe/haber, no asiento oficial; `draft_not_posted`.
- `analytics.py`: métricas, alertas explicables y snapshots.
- `report_routes.py`: dashboard y reportes PDF, PowerPoint con gráfico editable, HTML y SVG.
- Los datos posteriores marcan cálculos/informes como basados en información anterior.
- La diferencia operativa mostrada no es beneficio contable, base fiscal ni caja.

No mezclar cifras de Odoo con cifras locales duplicadas en el dashboard. Añadir procedencia, frescura y conciliación únicamente con contrato claro y pruebas.

---

## 7. Mapa de archivos y orden de lectura

### Leer primero

1. Este handoff.
2. `docs/odoo-adapter/CAMPAIGN.md`.
3. `docs/odoo-adapter/final-report.md`.
4. `docs/odoo-adapter/00-baseline.md`.
5. `docs/odoo-adapter/c01/{README,EVIDENCE,TESTS,RISKS,DECISIONS}.md` y `ci-evidence.json`.
6. `docs/odoo-adapter/c02/{README,EVIDENCE,TESTS,RISKS,DECISIONS}.md` y `static-checks.json`.
7. `docs/odoo-adapter/odoo19-source-map.md`, `odoo19-capability-matrix.md`, `odoo19-licensing.md`.
8. `infra/odoo/UPSTREAM.md` y `upstream-lock.json`.

### Código existente que debes inspeccionar antes de integrar

`README.md`, `pyproject.toml`, `.env.example`, `app.py`, `auth.py`, `models.py`, `storage.py`, `tax.py`, `engines.py`, `rules.py`, `territories.py`, `analytics.py`, `report_routes.py`, tests y frontend. Después, `typescript/index.ts`, `hono.ts`, `agents.ts`, `types/*`, `scripts/build.mjs` y `package.json`.

### Herramientas actuales de comprobación

- `scripts/verify_baseline.py`: verifica los 43 archivos congelados sin importar FastAPI ni abrir DB.
- `scripts/verify_odoo_source.py`: verifica hashes/contratos de fuentes Odoo sin ejecutarlo.
- `scripts/browser_check.py`: usa datos sintéticos y un servicio temporal para probar dashboard, escritorio/móvil, registro y descarga de PowerPoint.
- `.github/workflows/ci.yml`: instalación dev, unittest, Node, Playwright y capturas.
- `.github/workflows/odoo-baseline.yml`: inventario de baseline.
- `.github/workflows/odoo-source-audit.yml`: checkout sparse del SHA Odoo y 38 checks estáticos.

No hay todavía `odoo_bootstrap.py`, `odoo_smoke.py`, `odoo_reset_test.py`, Compose ni implementación de integración. Si los necesitas, créalos de verdad en la fase adecuada y documenta sus pruebas; no escribas instrucciones como si ya existieran.

---

## 8. Evidencias ejecutadas frente a pendientes

### 8.1 CI observada

C01 inicial:

- CI: <https://github.com/uniscrolliabrain-cloud/agntia-gestoria/actions/runs/42653348715>.
- Inventario: <https://github.com/uniscrolliabrain-cloud/agntia-gestoria/actions/runs/42653348825>.
- Log: 23 pruebas, 0 fallos, sin workaround; navegador desktop/mobile, registro y descarga aprobados.

C02 primera revisión:

- CI: <https://github.com/uniscrolliabrain-cloud/agntia-gestoria/actions/runs/42676011890>.
- Contratos estáticos: <https://github.com/uniscrolliabrain-cloud/agntia-gestoria/actions/runs/42676012171>.
- Inventario C01: <https://github.com/uniscrolliabrain-cloud/agntia-gestoria/actions/runs/42676012365>.

Último head C02 consultado antes de fusionar, `df989bef…`:

- CI: <https://github.com/uniscrolliabrain-cloud/agntia-gestoria/actions/runs/42676243998> — success.
- Fuente: <https://github.com/uniscrolliabrain-cloud/agntia-gestoria/actions/runs/42676244251> — success.
- Baseline: <https://github.com/uniscrolliabrain-cloud/agntia-gestoria/actions/runs/42676244638> — success.

Los links son evidencia histórica por revisión, no una garantía de cualquier commit posterior. Comprueba siempre el HEAD real del laptop y el SHA al que corresponde una ejecución. No sumes 38 comprobaciones estáticas y 23 unittest como si fueran 61 pruebas de integración Odoo.

### 8.2 Diagnósticos locales anteriores

El entorno anterior era Linux restringido con Python 3.12.14, Node 24.22.1, usuario sin privilegios y dependencias compartidas. Se observó:

- Instalación runtime editable offline: PASS.
- Extra dev offline: bloqueado porque no había pytest disponible; no se cambiaron dependencias para ocultarlo.
- Suite unittest estándar: timeout local en TestClient.
- Suite con ajuste temporal del selector exclusivamente en el proceso de tests: 23/23 PASS.
- Node build, sintaxis y artefactos sin cambios: PASS.
- Navegador local: socket denegado antes del arranque útil; CI sí lo ejecutó.
- Docker: daemon detectado pero socket denegado. Una solicitud posterior de acceso no llegó a ejecutarse y fue abortada; no se debe registrar como permiso concedido ni como prueba realizada.
- El entorno estuvo temporalmente indisponible y después volvió a permitir archivos/comandos.

Estos bloqueos pertenecen a ese entorno. No los extrapoles al laptop ni copies el workaround del selector como cambio de producción. Ejecuta primero los comandos estándar en Windows/CI. Si pasan, conserva esa evidencia limpia.

### 8.3 Lo que NO se ha ejecutado

No se ha arrancado Odoo, descargado una imagen para correrla, creado una base real de laboratorio, configurado un bot, llamado JSON-2, comprobado ACL reales, importado una factura Odoo, creado un borrador remoto, probado dos DB, restaurado un backup de Odoo ni ejecutado E2E A–E. No hay mediciones de p50/p95 o coste por tenant del adaptador.

---

## 9. Primer arranque en PowerShell: reproducir sin tocar datos reales

Estos comandos son una guía para el laptop y **no se han ejecutado allí**. Se han preparado para Windows PowerShell 5.1/PowerShell 7 evitando `&&`, dependencia de activación de venv y cambios globales de política. Comprueba las versiones locales y adapta rutas. No uses una terminal de producción ni un Docker remoto por accidente.

### 9.1 Inventario de herramientas

```powershell
$ErrorActionPreference = 'Stop'

function Assert-NativeSuccess {
    param([string]$Step)
    if ($LASTEXITCODE -ne 0) {
        throw "$Step fallo con exit code $LASTEXITCODE"
    }
}

Get-Command git -ErrorAction Stop
Get-Command py -ErrorAction Stop
Get-Command node -ErrorAction Stop

git --version
Assert-NativeSuccess 'git --version'
py --list
Assert-NativeSuccess 'py --list'
node --version
Assert-NativeSuccess 'node --version'
```

Python recomendado para reproducir: 3.12. El proyecto admite >=3.11. Para el SDK/build, utiliza una versión Node soportada, preferiblemente 24 como CI; el paquete exige >=22.13. Si no existe `py` pero sí una instalación adecuada de Python, usa su ejecutable explícito. No instales herramientas con administrador ni cambies PATH global sin atender las reglas del laptop.

### 9.2 Clonar limpio

```powershell
$WorkspaceRoot = Join-Path $env:USERPROFILE 'source'
New-Item -ItemType Directory -Force -Path $WorkspaceRoot | Out-Null
$RepoRoot = Join-Path $WorkspaceRoot 'agntia-gestoria'

if (Test-Path $RepoRoot) {
    throw 'Ya existe la carpeta. Inspecciona sus cambios y remotos antes de reutilizarla.'
}

git clone https://github.com/uniscrolliabrain-cloud/agntia-gestoria.git $RepoRoot
Assert-NativeSuccess 'clone Gestoria'
Set-Location $RepoRoot

git switch main
Assert-NativeSuccess 'switch main'
git pull --ff-only origin main
Assert-NativeSuccess 'pull main'
git status --short
git rev-parse HEAD
Assert-NativeSuccess 'leer HEAD'
git log -8 --oneline
```

Si ya hay un checkout con cambios, no ejecutar `reset --hard`, limpiar archivos ni forzar checkout. Revisar lo que es del propietario, crear una rama o worktree limpio y preservar modificaciones. No usar tokens pegados en la URL de `origin` ni imprimir configuración global de Git.

### 9.3 Crear venv y ejecutar baseline estándar

```powershell
py -3.12 -m venv .venv
Assert-NativeSuccess 'crear venv'
$Py = Join-Path $RepoRoot '.venv\Scripts\python.exe'

& $Py -m pip install -e '.[dev]'
Assert-NativeSuccess 'instalar desarrollo'

& $Py scripts/verify_baseline.py
Assert-NativeSuccess 'baseline congelado'

& $Py -m unittest discover -s tests -v
Assert-NativeSuccess 'unittest'

node typescript/scripts/build.mjs
Assert-NativeSuccess 'build TypeScript'
node --check agntia_gestoria/static/app.js
Assert-NativeSuccess 'sintaxis app.js'
node --check agntia_gestoria/static/dashboard.js
Assert-NativeSuccess 'sintaxis dashboard.js'

git diff --exit-code -- typescript/dist
Assert-NativeSuccess 'artefactos JS sin diferencias'
```

No es necesario activar `.venv`; usar `$Py` evita problemas de ExecutionPolicy. No ejecutar `Set-ExecutionPolicy Unrestricted`, desactivar TLS o instalar globalmente para sortear errores. Si las dependencias no se descargan, registra el fallo y resuelve red/certificados del entorno de forma correcta.

### 9.4 Navegador

```powershell
& $Py -m playwright install chromium
Assert-NativeSuccess 'instalar navegador Playwright'
& $Py scripts/browser_check.py
Assert-NativeSuccess 'browser check'
```

El script usa un servidor/DB temporales y fixtures, no datos del propietario. Conserva capturas de `test-results` como evidencia de esa revisión. No publiques capturas de una sesión real ni conviertas fixtures en cifras comerciales.

### 9.5 Estado Git y rama de continuación

```powershell
git status --short
git switch -c feat/odoo-c02-runtime-verification
Assert-NativeSuccess 'rama para verificacion pendiente'
```

Si el nombre ya existe, inspecciona su contenido; no lo sobrescribas. Es una continuación del gate pendiente de C02, no una afirmación de que C03 ya está aprobada. Mantén en PR separada cualquier trabajo de infraestructura necesario y etiqueta las dependencias reales de los gates.

---

## 10. Recuperar las fuentes Odoo exactas en Windows

No uses HEAD actual de 19.0 y luego digas que probaste el pin anterior. Las ramas se mueven. El pin se conserva en `infra/odoo/upstream-lock.json`.

```powershell
$Lock = Get-Content 'infra/odoo/upstream-lock.json' -Raw | ConvertFrom-Json
$OdooSha = $Lock.upstream.commit
$OdooReference = Join-Path $WorkspaceRoot 'odoo-19-reference'

if (Test-Path $OdooReference) {
    throw 'Referencia existente: comprobar que sea el repositorio esperado y que este limpio.'
}

git clone --filter=blob:none --no-checkout https://github.com/odoo/odoo.git $OdooReference
Assert-NativeSuccess 'clone referencia Odoo'
git -C $OdooReference config core.autocrlf false
Assert-NativeSuccess 'LF en la referencia local Odoo'
git -C $OdooReference sparse-checkout init --no-cone
Assert-NativeSuccess 'sparse init'

$SourcePaths = $Lock.sources |
    Where-Object { $_.repository -eq 'odoo/odoo' } |
    ForEach-Object { '/' + $_.path }
$SourcePaths | git -C $OdooReference sparse-checkout set --no-cone --stdin
Assert-NativeSuccess 'sparse paths'

git -C $OdooReference fetch --depth 1 origin $OdooSha
Assert-NativeSuccess 'fetch pin Odoo'
git -C $OdooReference checkout --detach $OdooSha
Assert-NativeSuccess 'checkout pin Odoo'
git -C $OdooReference rev-parse HEAD
Assert-NativeSuccess 'verificar HEAD Odoo'

& $Py scripts/verify_odoo_source.py --source-root $OdooReference
Assert-NativeSuccess 'contratos estaticos Odoo'
```

Precaución de Windows: Git puede convertir LF/CRLF según configuración. Los checks de fuente son por bytes; una conversión puede cambiar SHA-256 sin cambiar semántica. Para una referencia nueva dedicada, decide la política de fin de línea en **ese repositorio**, no globalmente, antes del checkout. Una opción es `git -C $OdooReference config core.autocrlf false` antes de materializar los archivos. Registra el ajuste y conserva bytes del upstream. No regeneres los hashes esperados para esconder CRLF.

No copies las fuentes Odoo al paquete propio ni las comprometas en Gestoría. Si el clon sparse falla por versión Git o red, corrige el procedimiento y documenta; no sustituir por archivos inventados. El verificador no necesita todas las dependencias de Odoo ni lo importa.

---

## 11. Docker Desktop: comprobación segura antes del laboratorio

El laptop puede resolver el bloqueo anterior, pero no se presume que tenga Docker configurado. El propietario solo ha confirmado acceso a PowerShell.

```powershell
Get-Command docker -ErrorAction Stop

docker version
Assert-NativeSuccess 'docker version'
docker context show
Assert-NativeSuccess 'docker context'
docker info --format '{{.OSType}}'
Assert-NativeSuccess 'tipo de contenedores'
docker compose version
Assert-NativeSuccess 'compose version'
```

Debe utilizarse Docker Linux local para las imágenes previstas. Si hay variables `DOCKER_HOST` o `DOCKER_CONTEXT` configuradas, no imprimas valores con posibles credenciales ni borres configuración a ciegas: determina si apuntan a producción/remoto y detente si no puedes confirmar el entorno local de prueba.

No ejecutes la receta Linux de `dockerd`, `sudo`, `/var/run/docker.sock` o dind en Windows. No cambies de contexto automáticamente a un host ajeno. Si Docker Desktop necesita WSL2/virtualización/instalación/reinicio, identifica el requisito y pide la aprobación del propietario para la modificación de sistema concreta cuando corresponda. No es un fallo del adaptador y no se arregla dándole permisos de administrador a todo.

### 11.1 Puertos y red del laboratorio

- PostgreSQL no debe exponerse públicamente.
- La red entre Gestoría y Odoo debe ser privada o de loopback explícito en desarrollo.
- Si se publica un puerto web para pruebas locales, usar `127.0.0.1:puerto:8069`, nunca `0.0.0.0:8069` por defecto.
- No abrir selector de bases a Internet; `list_db=False` y dbfilter comprobado en el laboratorio.
- Para varias DB en un mismo servidor, verificar el uso real de `X-Odoo-Database` y su relación con dbfilter; no suponer que basta un header para demostrar aislamiento.
- No usar `--network host` ni desactivar TLS para saltar bloqueos de red.
- Los nombres de DB, contraseñas y API keys reales no se guardan en Git. Fixtures claramente identificados y credenciales efímeras fuera de artefactos publicados.

### 11.2 Imagen fijada y problema pendiente de equivalencia

Referencias registradas:

- Core Odoo: `60657b50d171ddf84ab58717fdee5ac26031065b`.
- Documentación: `67e8ded4a03d7c53be4e2c4d53471678e9e9352e`.
- Receta oficial: `odoo/docker@f900094eb7492968332868d686caf22b966592ca`, `19.0`.
- Tag observado: `19.0-20261102`.
- Índice OCI: `sha256:5e755c725b3c43cf0be16d579904e1418300db3a2c44952f928eaddbcb0cc16d`.
- Manifest amd64: `sha256:08374de09bab5d80851c5709896aa49917e6c6a893b39025d6669db908e238b0`.
- Fuente de metadatos de imagen: `docker-library/repo-info@afb419bc04faac713edf97eda3d9b09c63ba3cd9`.

La imagen contiene un nightly del 02/11; el SHA de código auditado se fijó al consultar la rama el 09/11. **No está demostrada su identidad.** No pongas ambos en un reporte como si fueran el mismo artefacto.

Opciones a evaluar con evidencia: construir el laboratorio desde el SHA exacto con receta/dependencias reproducibles; o identificar de manera verificable el código real de la imagen y fijar esa referencia como objetivo de runtime, reauditar diferencias y conservar el pin anterior como histórico. No reemplazar silenciosamente un lock ni inventar un digest.

`MIN_PG_VERSION=13` en release.py es un mínimo declarado, no una prueba de una versión PostgreSQL concreta. Elegir y fijar versión/digest de PostgreSQL después de validar compatibilidad. No se dejó Compose listo porque esa comprobación no estaba hecha.

---

## 12. Laboratorio que debe existir antes de afirmar integración real

Crear artefactos reales de C03 cuando puedas ejecutarlos: `infra/odoo/compose.yaml`, configuración segura, `.env.example` sin secretos, scripts de bootstrap/reset/backup y documentación.

Requisitos mínimos:

1. Proyecto Docker con nombre inequívoco de test y volúmenes propios, distinto de cualquier instalación personal/productiva.
2. Odoo Community 19 fijado y PostgreSQL compatible fijado, con healthchecks, recursos razonables y volúmenes persistentes.
3. Dos bases sintéticas, por ejemplo `agntia_test_a` y `agntia_test_b`; no nombres de clientes.
4. Bot distinto por DB, con permisos mínimos y sin administración general en operaciones de negocio.
5. Inicialización administrativa de fixtures aislada de la credencial bot; no reutilizar admin como integración porque funcione más rápido.
6. Módulos base, contacts, account y l10n_es únicamente si se instalan efectivamente y se registra su estado/versión.
7. Verificar instalación con y sin account; una capacidad ausente debe quedar unsupported, no generar datos simulados.
8. Prueba negativa de DB/credencial/compañía intercambiadas: no basta que A funcione.
9. Backup y restore de DB y filestore, con checksum/registro reproducible y prueba de recuperación.
10. No publicar Odoo/DB al exterior ni montar todo el disco del laptop dentro de contenedores.

No ejecutar `docker compose down -v` en una carpeta cualquiera. Los scripts de reset deben exigir proyecto/nombres de test exactos, confirmación o parámetro de test explícito, y rechazar DB no prefijadas como test. No eliminar documentos locales para hacer pasar una importación.

### 12.1 Dependencia entre C02 y C03

La campaña pide en C02 observaciones de instalación real y en C03 formalizar el laboratorio. Hay una dependencia práctica que debes hacer explícita: preparar infraestructura de verificación para cerrar C02 no permite declarar C03 aprobada sin su evidencia. Puedes proponer PR de laboratorio dependiente, con estados precisos y sin introducir lógica de integración de fases posteriores. No marques C02 PASS solo porque su auditoría estática está fusionada.

---

## 13. Arquitectura objetivo y autoridades por dominio

```text
Owner / humano autorizado
    -> AgntiaPro (identidad, tenant, roles, policy, SOP, aprobaciones, Laia)
    -> SDK TypeScript/Hono interno
    -> FastAPI Gestoria (permisos, evidencias, fiscalidad acotada)
         -> SQLite local: conexiones, links, jobs, conflictos, outbox/inbox
         -> OdooAdapter Python JSON-2
              -> Odoo Community 19 + PostgreSQL, preferencia DB por tenant
```

| Dominio | Autoridad | Copia/proyección y regla |
| --- | --- | --- |
| Principal/tenant/capacidades | AgntiaPro cuando se integre | Gestoría recibe principal verificado, no claims de un LLM |
| Hechos fiscales declarados y revisión | Gestoría | Odoo puede aportar referencias, no sobrescribir aprobación |
| Contactos/facturas/diarios/asientos ERP | Odoo | Gestoría conserva snapshots y procedencia |
| Documento original | Custodio declarado por objeto | Hash/referencia; duplicar binario solo cuando procede |
| Cálculo 303/130 admitido | Gestoría | No sustituir por un impuesto/configuración Odoo |
| SOP/eventos/rota | Runtime organizativo de AgntiaPro | Gestoría expone capacidades/eventos; no segundo scheduler |
| Pago y conciliación bancaria | Proveedor autorizado correspondiente | Fuera de escritura del MVP |

Ante un cambio concurrente entre autoridades, crear conflicto y pedir revisión; no hacer last-write-wins silencioso. Los campos fiscales no resueltos siguen no resueltos. Un usuario con acceso a la DB no obtiene por ello autoridad para aprobar fiscalidad.

### 13.1 Tres identidades que nunca deben confundirse

- `gestoria_company_id`: UUID hexadecimal de 32 caracteres.
- `odoo_company_id`: entero de `res.company` dentro de una DB.
- `tenant_id`: identificador opaco del sistema organizativo, cuando se integre.

Además, `connection_id` identifica un backend aprobado. La DB es parte de la identidad del backend, no un parámetro libre de cada consulta. Mismo nombre o NIF no permite mapear ni deduplicar automáticamente empresas.

---

## 14. Hallazgos upstream que condicionan la implementación

### 14.1 JSON-2 de verdad

La ruta es `POST /json/2/<model>/<method>`, bearer API key, parámetros por nombre, ids para recordsets y context cuando proceda. `X-Odoo-Database` es configuración del servidor/registro aprobado. El retorno exitoso es JSON directo, no asumir un envelope JSON-RPC `result` de versiones antiguas.

El controlador usa resolución de método público y validación de firma. Que un método sea público no significa que el negocio permita al agente ejecutarlo. Debe existir una allowlist cerrada de parejas modelo/método y, hacia usuarios/agentes, capacidades nominadas de negocio, no passthrough ORM.

Cada llamada es una transacción SQL independiente. `search_read` evita search+read en llamadas separadas. Create y action_post nunca deben combinarse como si fueran una transacción distribuida. Action_post está prohibido en este MVP de todas formas.

### 14.2 Contabilidad y doble cómputo

- `account.move.state`: draft, posted, cancel.
- `move_type` distingue factura/abono de cliente/proveedor y asientos `entry`.
- `invoice_line_ids` es un subconjunto de `line_ids`, pero incluye producto, sección, subsección y nota.
- `display_type` también distingue cuotas, contrapartidas, redondeo, descuentos y variantes no deducibles.
- No sumar todas las líneas contables ni trasladar total de factura a cada línea.
- Las cantidades, descuentos, subtotal, total, moneda e impuestos compuestos deben reconciliarse con la factura, no estimarse de forma independiente.
- `out_refund`/`in_refund` no son una venta/gasto normal positivo; definir signos y procedimiento de rectificación explícitamente.
- `invoice_date`, `date` y devengo fiscal no son sinónimos.

### 14.3 Compañías y ACL

`account.account` usa `company_ids` en plural en el upstream fijado. Las reglas de algunas entidades usan `parent_of`, no pertenencia exacta. Las reglas de partners permiten contactos globales y excepciones para usuarios internos. Por tanto, no confiar en las ACL por sí solas para demostrar aislamiento del tenant.

Discovery debe verificar campos efectivos, compañía vinculada, usuario y allowed_company_ids; el adaptador debe aplicar además su binding exacto. No aceptar context ni dominios del texto del agente. No leer ni devolver datos de otra empresa para explicar por qué se denegó la petición.

### 14.4 Impuestos y España

`account.tax` tiene tipos agrupados, fijos, porcentaje y división, puede incluir el impuesto en precio, depender de compañía y tener subimpuestos. Un `amount=21` no certifica IVA; un impuesto negativo no se puede tratar automáticamente como retención soportada sin analizar su naturaleza y procedencia.

`l10n_es/__manifest__.py` declara datos de varios modelos e incluye mod420. Eso demuestra que hay referencias de localización en el árbol, no instalación, exactitud, soporte de cada operación canaria o presentación oficial. La ruta real lleva `__manifest__.py`; la ruta `manifest.py` citada inicialmente era incorrecta.

### 14.5 Licencias

Core y los manifiestos inspeccionados declaran LGPL-3. Hay componentes externos que pueden tener otras licencias. OCA requiere revisión por addon/versión/dependencias; no asumir una licencia uniforme ni instalar todo l10n-spain. La integración será por API sin copiar upstream al paquete MIT. Si se crea bridge, decidir licencia compatible y obligaciones en C17.

---

## 15. Contratos de datos a implementar en C04

Los siguientes son **contratos objetivo**, no DTOs actualmente disponibles. Implementarlos con Pydantic/DTOs tipados, `extra='forbid'`, límites explícitos, enums cerrados y serialización estable. Decimales monetarios en strings; rechazar NaN/Infinity y conversiones silenciosas desde float en las fronteras que lo requieran.

### 15.1 Connection pública

```json
{
  "connection_id": "uuidhex32",
  "gestoria_company_id": "uuidhex32",
  "tenant_id": "opaque-tenant-id",
  "provider": "odoo_community",
  "provider_version": "19.0",
  "base_url_ref": "server-endpoint-id",
  "database_name_ref": "server-database-id",
  "credential_ref": "secret-manager-key",
  "odoo_company_id": 1,
  "state": "pending_validation",
  "capabilities": ["contacts.read", "invoices.read"],
  "created_at": "ISO-8601",
  "revision": 0
}
```

No serializar el secreto real. Ni siquiera las referencias o nombres internos deben devolverse a viewer/agent si no hacen falta. Configuración de URL/DB/secretos solo del servidor. Standalone compatible requiere modo explícito; integración con AgntiaPro exige tenant autenticado, no un campo autodeclarado.

### 15.2 ExternalObjectLink

Identificar por conexión, modelo, ID técnico y clase local. Guardar `remote_write_date`, hash canónico, mapping_version, last_seen_at y sync_status. Índice único de la cardinalidad acordada; para líneas, ID de factura/línea cuando sea necesario. El número visible de factura no es identidad global.

Una relectura idéntica debe resultar unchanged. Un cambio de origen no puede sobreescribir un registro revisado. Un objeto desaparecido no debe borrar historia local. Una misma idempotency key con payload distinto debe producir 409.

### 15.3 ImportedEconomicFact

Campos no resueltos deben permanecer sin resolver. Ejemplo de forma, no clasificación universal:

```json
{
  "external_id": "odoo:connection:model:record:version",
  "operation_date": "2026-11-01",
  "kind": "income",
  "description": "Descripcion normalizada pendiente de revision",
  "tax_kind": "other",
  "base_amount": "100.00",
  "tax_amount": "21.00",
  "withholding_amount": "0.00",
  "document_ids": [],
  "category": "other",
  "vat_treatment": "other",
  "tax_rate": null,
  "deductible_tax_amount": null,
  "deductible_irpf_amount": null,
  "classification_notes": "Origen Odoo; pendientes fecha fiscal, justificante y clasificacion"
}
```

Solo usar IVA/IGIC y tipos si el mapeo y contexto están inequívocamente probados. Siempre status local unverified. Una factura draft de Odoo aporta una propuesta/evidencia ERP, no acredita una factura emitida ni basta por sí sola como soporte fiscal definitivo. El vertical slice puede recorrer revisión y cálculo únicamente cuando el soporte y los hechos cumplan de verdad el ámbito del motor; no fabricar elegibilidad para que la demo llegue al final.

### 15.4 OperationEnvelope

Campos: schema_version, tenant_id, company_id, actor_id, capability, correlation_id, causation_id, idempotency_key, approval_id, expected_revision, dry_run y payload validado.

El servidor genera o verifica principal, scopes e IDs de correlación. Un LLM no puede elevarse escribiendo actor_id=owner, tenant_id de otro cliente, allowed_company_ids, model/method o approval_id inventado.

Resultado: status discriminado, local_id, remote_id, warnings, evidence, source_hash, mapping_version, retryable y reconciliation_required. No incluir payload remoto crudo, secretos o DSN en un error público.

### 15.5 Otros DTOs

CapabilityReport, SyncCursor, SyncJob, ImportPreview, Conflict, Money y EvidenceRef. Schema versionado y pruebas Python↔TS. No añadir campos ambiguos a TaxRecord para acomodar un caso sin justificar su semántica. Preferir procedencia/bindings separados con migración aditiva.

---

## 16. Migraciones, historia e idempotencia

C05 debe añadir tablas como provider_connections, external_links, sync_jobs, sync_cursors, integration_outbox, integration_inbox, idempotency_keys e integration_conflicts, con FKs y claves compuestas por empresa/tenant/conexión según la cardinalidad real. Son nombres propuestos, no tablas actuales.

Requisitos:

- Migraciones versionadas y aditivas, dentro de transacción apropiada; cuidado con `executescript` y sus implicaciones de commit en SQLite.
- Backup previo de una copia de DB de test y prueba de upgrade con datos/auditoría antiguos intactos.
- No almacenar API keys ni secretos en JSON.
- Lock de escritura y pruebas de concurrencia con BEGIN IMMEDIATE.
- No asumir que un worker y WAL hacen al servicio distribuido.
- No downgrade destructivo ni restauración automática sobre una DB sin autorización.
- Outbox/inbox y claves idempotentes persistentes para cruzar SQLite/PostgreSQL de Odoo.
- Cursor solo avanza después del commit local que guarda datos/links/evidencias.
- Guardar intentos fallidos de mutación con resultado seguro y correlación sin revelar PII.

### 16.1 Exactly-once no existe por declararlo

Tras un timeout de escritura, el estado remoto puede haberse confirmado. No reintentar create a ciegas. La operación pasa a reconciliación, consulta por identidad/idempotency key remota de negocio y resuelve antes de decidir otro intento. Una clave almacenada solo en SQLite no evita duplicar un create que Odoo confirmó antes de caer la respuesta.

Si la API estándar no permite esas garantías para factura draft, analizar bridge transaccional en C17 antes de habilitar write-back. El bridge no debe ser un ejecutor genérico ni utilizar sudo para ocultar ACL deficientes.

### 16.2 Cursor incremental

Diseñar (write_date,id), orden estable, overlap para empates, relectura, reloj remoto y barridos periódicos. Una página duplicada no duplica datos. Un remoto borrado/archivado genera revisión, no borrado contable local. Si un registro cambia durante paginación o después de una revisión humana, bloquear y crear conflicto.

Estados de jobs previstos: pending, running, succeeded, failed, reconcile_required, blocked; leases con caducidad y presupuesto de retry/dead-letter. Revalidar permisos también en el worker, no solo al crear el job.

---

## 17. Transporte HTTP y seguridad de frontera

Añadir httpx como dependencia runtime cuando se implemente C07; actualmente aparece como dependencia dev. Elegir sync o async coherente con las rutas y el modelo de concurrencia, sin mezclar clientes/bucles de forma accidental.

### 17.1 Configuración remota aprobada

- Host/scheme/puerto/DB/cuenta definidos por administrador en servidor.
- HTTPS fuera de excepciones locales de test explícitas.
- Allowlist de hosts y redes por despliegue; rechazar metadata IP, credenciales en URL, fragmentos, esquemas distintos y redirecciones.
- No aceptar URL/modelo/método/context/dominio arbitrario en herramientas de agentes.
- Revisar DNS rebinding y TOCTOU: resolver y validar una IP al principio no garantiza que el transporte conecte después al mismo destino. Definir estrategia de transporte/red que mantenga validación, hostname y TLS/SNI correctos.
- Considerar IPv6, IPv4-mapped IPv6, loopback y formatos alternativos; no comparar solo strings con una IP prohibida.
- `trust_env` y proxies deben decidirse explícitamente para la conexión aprobada; no filtrar bearer a un proxy no previsto ni desactivar la política de red del entorno.

### 17.2 Robustez

Timeouts por tipo de operación, pool controlado, límite de bytes leído antes de parsear, no redirects y errores normalizados. Lecturas pueden usar retry con presupuesto/backoff/jitter y circuit breaker; las escrituras requieren política de reconciliación, no retry automático por ser POST.

Las respuestas Odoo pueden contener trazas, nombres de DB, mensajes con datos y errores HTML del proxy. No devolverlos íntegros. Log estructurado con categoría, IDs opacos y resultado. Error 401/403 jamás activa fallback admin.

Para importes JSON, evitar perder precisión por parsear primero a float y luego convertir a Decimal. Verificar la representación del protocolo real; usar parseo decimal cuando corresponda y reglas de redondeo conciliadas con moneda/Odoo. No corregir diferencias silenciosamente con tolerancias arbitrarias.

### 17.3 Documentos

Binarios backend a backend, metadatos primero. Descarga explícita con límite de bytes, tipo real, hash, nombre generado, almacenamiento/cifrado y escaneo configurable si existe. La ausencia de antivirus debe quedar como limitación, no como escaneo aprobado. No meter instrucciones de un PDF/CSV en el contexto de sistema de un agente.

Exportar CSV/Excel exige proteger strings con fórmulas al abrirse en hojas de cálculo, sin corromper importes numéricos. XML/HTML deben tratarse como contenido no confiable, no páginas activas ejecutadas en el producto. No exponer rutas locales, bearer, DSN, nombres internos innecesarios ni URLs firmadas en reportes compartibles.

---

## 18. API, errores y SDK TypeScript/Hono

### 18.1 Mantener compatibilidad

No romper exports `@agntia/gestoria`, `/hono` y `/agents`. El paquete tiene fuentes TS, JS compilado versionado en `typescript/dist` y declaraciones `.d.ts` en `typescript/types`.

El build actual solo procesa `index`, `agents` y `hono` con stripTypeScriptTypes. Cuando añadas `odoo.ts` y `odoo-agent-tools.ts`, ampliar build, exports, declaraciones y tests. No publicar tipos que importen `.ts` de manera incompatible con tsconfig ordinarios si puedes exportar declaraciones con imports `.js`.

El cliente actual devuelve unknown y acepta Record para varias herramientas; C18 debe añadir DTOs y validación runtime en fronteras. No se ha instalado el paquete dentro de `agente`, ni hay permiso para hacerlo todavía.

### 18.2 Hono no es una puerta ORM

El adaptador Hono actual filtra por prefijo y métodos. Las operaciones Odoo deben añadirse mediante allowlist exacta ruta/método y funciones de negocio, sin proxy `POST /odoo/{model}/{method}`. El anfitrión resuelve el principal autenticado y usa credenciales acotadas por actor/empresa. No usar un owner global en todas las peticiones.

Los tokens se quedan en backend. La UI pública no recibe credenciales Odoo. Los uploads/descargas necesitan rutas backend específicas; no meterlos por la ruta JSON genérica para que parezcan funcionar.

### 18.3 Endpoints propuestos, aún NO implementados

```text
GET  /api/companies/{cid}/integrations/odoo/capabilities
GET  /api/companies/{cid}/integrations/odoo/health
POST /api/companies/{cid}/integrations/odoo/imports/preview
POST /api/companies/{cid}/integrations/odoo/imports
GET  /api/companies/{cid}/integrations/odoo/jobs/{job_id}
GET  /api/companies/{cid}/integrations/odoo/conflicts
POST /api/companies/{cid}/integrations/odoo/conflicts/{id}/resolve
POST /api/companies/{cid}/integrations/odoo/partners/dry-run
POST /api/companies/{cid}/integrations/odoo/partners/commit
POST /api/companies/{cid}/integrations/odoo/invoice-drafts/dry-run
POST /api/companies/{cid}/integrations/odoo/invoice-drafts/commit
```

Las operaciones largas deben devolver 202 y job scoped, no mantener Hono esperando 30 segundos una importación grande. La semántica de job no puede esconder una acción ya confirmada con efectos externos.

### 18.4 Semántica de error objetivo

```json
{
  "code": "reconciliation_required",
  "message": "El resultado remoto debe verificarse antes de reintentar",
  "correlation_id": "opaque-id",
  "retryable": false
}
```

Códigos HTTP acordables: 400 entrada, 401 autenticación, 403 rol/capacidad, 404 ajeno/inexistente sin filtrar, 409 revisión/idempotencia/conflicto, 422 validación de negocio, 424 dependencia/capacidad no disponible si se adopta en contrato, 429 límite, 502 respuesta inválida, 503 proveedor caído, 504 timeout. No cambiar la semántica de las rutas antiguas de forma accidental al normalizar las nuevas.

### 18.5 Aprobación

Dry-run calcula diff, hash de propuesta, coste/riesgo declarado, caducidad y evidencia. Commit exige la revisión esperada, key estable y aprobación válida vinculada a la propuesta, empresa y actor autorizado. Cualquier cambio de contenido invalida aprobación.

En standalone: implementar un adapter de aprobación explícito, o denegar las escrituras sensibles hasta disponer del servicio. No inventar un approval_id ni tratar un checkbox de un agente como aprobación humana.

---

## 19. Campañas restantes, entregables y gates concretos

### C03 — Laboratorio reproducible

Entregar Compose/configuración/scripts reales, DB A/B, bots, módulos, health, backup/restore y prueba de cruce. Gate: arranque limpio reproducible y restauración comprobada. No usar datos reales para obtener evidencia rápida.

### C04 — Contratos tipados

Crear paquete `integrations` con contratos, errores y DTOs Odoo. Verificar JSON Schema, round-trip, campos desconocidos, IDs, ISO, decimales/no finitos y estados discriminados. Gate: contrato estable testeado; no añadir transporte real antes de fijar frontera y policy.

### C05 — Persistencia aditiva

Migraciones bajo transacción, tablas/índices/FKs, respaldo, upgrade de copia antigua, rollback de fallo y pruebas de concurrencia/WAL. Gate: historia original intacta y reanudación coherente. Modificar storage mínimamente; justificar su interacción con el baseline congelado.

### C06 — Registro/secretos/policy

Conexiones server-side por empresa/tenant y referencias a secreto. Alta/rotación/desactivación seguras, sin devolver secreto ni permitir URL libre. Gate: pruebas cross-tenant, SSRF y centinelas de secretos; ninguna consulta Odoo antes de autenticar y autorizar el scope.

### C07 — Transporte JSON-2

Cliente con límites/errores/retry seguro/circuit breaker. Mock transport más contratos reales Odoo. Gate: headers correctos, respuestas directas, HTML/oversize, 401/403 y errores sanitizados. No retry ciego de create.

### C08 — Discovery

Versión, usuario, compañía, módulos y fields_get/ACL reales. Guardar CapabilityReport con fecha y evidencia, invalidar ante cambios. Gate: sin account → invoices.read unsupported; permisos insuficientes fallan cerrado. Un HTTP 200 no es capacidad demostrada.

### C09 — Binding y aislamiento

Owner vincula conexión aprobada a compañía exacta, con comprobación fiscal asistida si falta/diverge. Gate: intercambios A/B de conexión, credencial, DB y company_id bloqueados antes de exponer datos; cero filtraciones de metadatos ajenos.

### C10 — Partners

Paginación id ascendente, campos mínimos, preview y links. Gate: 1.000+ fixtures sin pérdidas/duplicados, Unicode, nombres iguales, globales y compañía ajena; repetición idéntica unchanged. No deduplicar por nombre/NIF de forma autónoma.

### C11 — Facturas

Filtrar move_type/state, identificar líneas reales y reconciliar totales por moneda/factura. Gate: 0/4/10/21, exento, retenciones, abonos, descuentos, impuestos incluidos/compuestos y moneda distinta; casos ambiguos mapping_blocked. No convertir estos casos en reviewed.

### C12 — Preview/staging/importación

Flujo discover → read → normalize → preview → validate → stage → import. Procedencia completa, hashes, versión del mapper y documentos pendientes. Gate: replay sin duplicados, cambio remoto crea conflicto, lote fallido sin importación parcial inadvertida y sin overwrite de revisados.

### C13 — Sync/jobs/reconcile

Cursor estable, overlap, watermark tras commit, leases, presupuesto de reintentos y barridos. Gate: crash antes/después de commit, páginas duplicadas y concurrentes, borrados/archivados, recuperación sin pérdidas. No declarar exactly-once sin garantías efectivas.

### C14 — Adjuntos

Primero metadatos; descargar explícitamente con controles de tamaño/tipo/hash/custodia y capacidad de escaneo declarada. Gate: MIME falso, archivo corrupto/grande, ruta maliciosa, cruce de empresa y red fallida. Original recuperable y no convertido en instrucciones del agente.

### C15 — Contactos write-back

Campos permitidos, expected_remote_write_date, dry-run y aprobación/policy. Gate: misma key/payload mismo resultado; payload distinto con misma key 409; edición remota bloquea; timeout incierto se reconcilia. No unlink ni identificación por simple nombre.

### C16 — Factura draft remota

Partir de invoice_draft local, validar diario/partner/taxes/cuentas por IDs de la compañía, calcular diferencias y comprobar estado remoto draft. Gate: totales conciliados y replay seguro, sin post/email/pago/número fiscal emitido. Si no hay atomicidad/idempotencia suficiente, no habilitar create todavía.

### C17 — Bridge solo si es necesario

Método de negocio transaccional mínimo con key única remota, ACL y compañía explícita; sin sudo ni execute genérico. Gate: concurrencia de dos peticiones crea un solo draft, excepción revierte todo y multiempresa aislada. Si no hace falta, registrar decisión de omitirlo con evidencia.

### C18 — Exposición API/SDK

Rutas nominadas, errores uniformes, DTOs Python/TS, Hono con allowlist exacta y exports compatibles. Gate: contratos entre lenguajes, scopes/revisiones/approvals y rutas antiguas sin regresión. Ningún token en navegador.

### C19 — Tools, eventos y SOP

Tools de lectura/propuesta, sin aprobación humana ni ejecución arbitraria. Definir eventos interoperables y documentación de integración posterior; no aplicar wiring a `agente`. Gate: agente sin elevación, briefing basado en hechos/evidencia y ausencia de actividad ficticia.

### C20 — Hardening y piloto

Ejecutar E2E A–E, fallos distribuidos, seguridad, restore, métricas, manuales y smoke/reconcile. Gate: escenarios críticos completos, límites documentados y demo reproducible con dos DB. Producción necesita aceptación expresa; no basta una CI verde de mocks.

Por fase: rama/PR propia, README/EVIDENCE/TESTS/RISKS/decisiones, SHA y logs sanitizados. No crear veinte carpetas con PASS vacío. No avanzar porque el siguiente bloque de código sea más entretenido que resolver un gate fallido.

---

## 20. Matriz de pruebas que no se puede omitir

### 20.1 Unitarias y de contrato

DTOs estrictos, decimales/no finitos/floats, signos, fechas, normalización canónica, hashes, identidad externa y versiones. Mapeo de move_type/display_type, descuento, composición de impuestos, moneda y refunds. Clasificación desconocida sigue desconocida. Un registro importado no se revisa solo.

Cursor con write_date empatado, reordenación y overlap. Key idempotente mismo payload → mismo resultado; payload distinto → conflicto. Hashes de auditoría: previous_hash, contenido, secuencia y verificación sin afirmar WORM legal. Métodos o context arbitrarios deben rechazarse en frontera.

### 20.2 Odoo real

Instalación limpia fijada, con/sin account y l10n_es; bot mínimo y bot insuficiente. Partner/search_read paginado y compañía exacta. Facturas draft/posted/refunds, líneas técnicas, taxes y journals. Error JSON directo frente a error HTML. Crear draft y provocar fallo para comprobar rollback y estado final, no solo respuesta HTTP.

### 20.3 Seguridad

A solicita connection_id B → 404 sin revelar existencia. A intenta odoo_company_id B → bloqueo antes de HTTP. agent intenta revisar → 403; viewer intenta import/write → 403. Key revocada → degraded, sin loop infinito ni fallback admin. URL metadata IP, redirect, DNS/IP no aprobados y context injection → rechazados.

Centinelas de secreto: assert de ausencia en logs, error JSON, exportación, reportes, eventos, repr de excepción y payloads de herramientas. No usar un secreto real para el centinela. No publicar documentos/capturas reales para demostrar que un test existe.

### 20.4 Fallos distribuidos

Caída Odoo durante lectura conserva snapshot anterior marcado stale. Caída SQLite no avanza cursor. Crash outbox antes de HTTP se recupera. Crash después de HTTP antes de ACK requiere reconciliación remota. No duplicar tras timeout. Cambios remotos posteriores a revisión no pisan la evidencia y dejan snapshots/cálculos stale.

### 20.5 Casos E2E A–E

A. Autónomo común: contacto/factura borrador Odoo → preview → import unverified → soporte documental adecuado → revisión humana → cálculo solo con ámbito exacto y hechos confirmados → reporte/briefing con fuentes. La existencia de una factura borrador no debe fingir una factura fiscal emitida.

B. SL Canarias: importación y preparación territorial; IGIC solo si demostrado; motor común 303/130 bloqueado, sin intento de presentación. Explicar lo pendiente.

C. Dos DB y dos compañías Gestoría, humanos con scopes separados y agentes. Misma razón social ficticia no une identidades. Cero contaminación.

D. Cambio remoto tras revisión: conflicto y stale; original preservado; no overwrite silencioso.

E. Replay de creación draft, incluido timeout tras confirmación remota: exactamente un draft, un link válido e historia de intentos. Si no puedes probarlo, escritura deshabilitada.

---

## 21. Briefing de Laia, eventos y rota: contrato, no scheduler nuevo

Eventos objetivo: `gestoria.odoo.sync.completed`, `.conflict.detected`, `.invoice_draft.created`, `.review.required`, `.connection.degraded`. Envelope con schemaVersion, ID, source, tenantId, companyId, correlationId, causationId, occurredAt y referencias mínimas.

Payload ejemplo: connectionId/jobId, imported/unchanged/conflicts y evidenceIds. No incluir nombres de clientes, documentos, bearer, DSN ni nombres internos de DB que no sean necesarios.

Rota prevista en horario de empresa:

- Mañana: salud/sync, novedades reales y documentación pendiente.
- Cierre diario: acciones efectivas, bloqueos y aprobaciones con evidencia.
- Semanal: Juan revisa excepciones/documentos; Antonio analiza finanzas con fuentes fiables; Marco ejecuta SOPs autorizados.
- Mensual: cierre/preparación, informe, riesgos y calendario oficial verificado.

La programación y distribución profesional de trabajo corresponde al runtime de `agente`. Gestoría no debe crear un segundo scheduler para cubrir una pieza no comprobada. Entregar contrato/simulación etiquetada y patchset propuesto, no modificar `agente` sin aprobación.

Un briefing debe distinguir hecho confirmado, dato sin revisar, inferencia/regla y decisión pendiente. No llamar caja al saldo de ingresos menos gastos ni afirmar que un impuesto está presentado porque un caso esté done.

---

## 22. Datos locales, backups y privacidad

No hay datos reales de clientes usados en esta campaña. Los ejemplos de informes se generaron con datos ficticios y se guardaron fuera del repo. No son necesarios para el adaptador ni deben importarse como datos del usuario.

SQLite y documentos originales no deben subirse a GitHub. `.env`, `.venv`, bases, PDFs generados y backups se mantienen fuera de Git según política. Revisa `git status` antes de cada commit; un `git add .` sin inspección puede incluir nuevos ficheros sensibles que aún no estén ignorados.

### 22.1 Backup coherente de una copia de desarrollo

Solo cuando exista una DB de desarrollo y se haya confirmado su ubicación. Detener escrituras para respaldar conjuntamente DB y documentos con consistencia; usar la API backup de SQLite, no una copia aislada del fichero `.sqlite3` ignorando WAL. Este ejemplo es una receta no ejecutada en el laptop y no autoriza leer/copiar producción.

```powershell
$BackupRoot = Join-Path $env:LOCALAPPDATA 'AgntiaGestoria\backups-dev'
New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null
$env:AGNTIA_BACKUP_DESTINATION = $BackupRoot

@'
import os, sqlite3
from datetime import datetime, timezone
from pathlib import Path
source = Path(os.environ.get('GESTORIA_DATA_DIR', './data')) / 'gestoria.sqlite3'
if not source.is_file():
    raise SystemExit('No existe la DB de desarrollo seleccionada; no se crea una vacia')
destination = Path(os.environ['AGNTIA_BACKUP_DESTINATION'])
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
target = destination / ('gestoria-dev-' + stamp + '.sqlite3')
if target.exists():
    raise SystemExit('Ya existe un backup con ese timestamp; no se sobrescribe')
with sqlite3.connect(source.resolve().as_uri() + '?mode=ro', uri=True) as src:
    with sqlite3.connect(target) as dst:
        src.backup(dst)
print('Backup SQLite completado en la carpeta local de desarrollo')
'@ | & $Py -
Assert-NativeSuccess 'backup SQLite desarrollo'
Remove-Item Env:AGNTIA_BACKUP_DESTINATION
```

Antes de automatizar este ejemplo, verifica rutas, colisiones de timestamp, permisos y restauracion en Windows. El fragmento Python se comprobo aqui solo con una DB sintetica temporal en Linux; el bloque PowerShell no se ejecuto en Windows. No sobrescribir backups; verificar checksum y restore. Completar copia coherente de documentos/filestore bajo parada de escrituras y cifrado adecuado: el backup SQLite solo no es una copia íntegra del expediente.

La conservación documental se decide por clase y obligación, no por borrar todo a los cuatro o seis años. Los registros de hash ayudan a detectar cambios, pero un administrador puede reescribir una base entera; no son firma legal ni archivo inmutable certificado.

---

## 23. Cuidado con el baseline congelado y cambios legítimos futuros

El verificador C01 comprueba hashes de 43 archivos originales. C02 y este handoff no los modifican. Cuando C05 cambie storage.py o C18 registre un router en app.py, el verificador fallará de manera esperable: está señalando un cambio del baseline, no prohibiendo evolucionar el producto.

No arreglarlo borrando el workflow, cambiando todos los hashes automáticamente o añadiendo una exclusión genérica. Diseñar una evolución revisable de esa política: baseline histórico inmutable más cambios permitidos por archivo, hash esperado, ADR, PR y no-regresión. Mantener protección estricta de las fórmulas/territorio/revisión según mandato. La aprobación de un cambio legítimo no autoriza silenciar cualquier diferencia futura.

Los archivos particularmente protegidos son `engines.py`, `rules.py`, `territories.py`, `data/legal_sources.json`, review/close de casos y analytics salvo procedencia/frescura justificada. Si hace falta tocarlos, justificar en ADR, añadir tests y pedir la revisión explícita que ordenó el propietario. No mezclar una corrección fiscal no solicitada con el adaptador.

---

## 24. Lista de riesgos abiertos y cómo cerrarlos

| Riesgo | Estado actual | Evidencia necesaria |
| --- | --- | --- |
| Fuente de imagen distinta del SHA | No resuelto | Correspondencia verificable o build desde SHA exacto |
| Docker en laptop | No comprobado | Contexto local Linux, daemon/Compose y laboratorio sintético |
| Tenant/principal AgntiaPro | No integrado | Contrato autenticado, scope y pruebas; no payload de LLM |
| Bot mínimo | No creado/probado | ACL reales positivas y negativas sin admin de negocio |
| Partners compartidos | Observado en fuentes | Filtros/policy/binding y tests de no filtración |
| company_ids plural | Observado | DTO/discovery/domino Odoo 19 correctos |
| Mapeo de líneas/taxes | No implementado | Conciliación por factura, estados/signos/moneda |
| Deductibilidad/fecha fiscal | No inferible por ERP | Revisión competente, hechos y documentos |
| Idempotencia tras timeout | No implementada | Replay/crash con reconciliación remota probada |
| Aprobación humana | Solo local existente | Adapter explícito para efectos externos o write deshabilitado |
| Adjuntos peligrosos | Integración pendiente | Límite/tipo/hash/escaneo/política y tests |
| Auditoría verificable | Hash local existente, extensión pendiente | Verificador, correlación y evidencia de intentos |
| RGPD/cifrado/restauración | No desplegado | Controles reales de almacenamiento y restore test |
| CI verde vs runtime | Distintos niveles | No equiparar checks de fuente o mocks con E2E Odoo |
| Cobertura territorial | Perfiles, no motores universales | Matriz por módulo/ejercicio/administración y reglas validadas |
| Coste | Sin medición del adaptador | Recursos/operaciones por tenant con hipótesis y medición |

### Stop conditions

Detener la fase ante fuga cross-tenant, publicación posible, error fiscal, impuesto/territorio ambiguo, bypass de aprobación, pérdida de auditoría, duplicación incierta o secreto expuesto. Corregir y documentar antes de continuar. No maquillar el gate como PASS ni usar más privilegios para evitar el problema.

---

## 25. Ruta recomendada para la próxima sesión en el laptop

### Primer bloque: conocer el terreno

- Leer instrucciones locales y este documento.
- Comprobar remoto, branch, HEAD y estado limpio sin borrar trabajo.
- Ejecutar baseline estándar y guardar versiones/resultados por SHA.
- Verificar fuentes fijadas y reproducir 38 checks sin modificar hashes.
- Comprobar Docker Linux local y requisitos WSL2 sin cambiar configuración global de forma automática.

### Segundo bloque: desbloquear pruebas reales

- Acordar mediante ADR la relación entre código fijado e imagen del laboratorio.
- Crear infraestructura mínima aislada, con dos DB/bots de fixture.
- Verificar módulos y contrato JSON-2 con credenciales mínimas y datos sintéticos.
- Añadir pruebas negativas de DB/compañía/usuario y errores sin filtrar secretos.
- Ejecutar backup/restore antes de afirmar reproducibilidad.
- Actualizar C02/C03 con logs y resultados reales. No declarar capacidad supported si sigue unknown.

### Tercer bloque: fundamento del adaptador

Solo tras resolver los gates anteriores: contratos C04, migraciones C05, registro/policy C06 y transporte C07, cada uno con rama/PR y evidencia. No empezar write-back antes de lectura, binding, staging y estrategia de reconciliación.

### Si no hay Docker operativo

Resolver el requisito concreto con el propietario o entorno autorizado. Puedes avanzar en documentación y pruebas puras de contratos que no simulen integración, pero no declarar fases cerradas ni crear veinte módulos vacíos. Comunica claramente el bloqueo. No pedir otra vez permiso para leer el repo, crear una rama o ejecutar una prueba ya autorizada.

---

## 26. Formato de informe que espera el propietario

Un informe útil debe permitir verificar lo que se hizo y lo pendiente:

1. Fase y resultado PASS/BLOCKED/NOT VERIFIED, separados para fuente, mocks y runtime.
2. Rama, PR, head y base SHA; merge solo si autorizado y observado.
3. Archivos afectados y razón; fórmulas y datos protegidos conservados o ADR del cambio.
4. Comandos ejecutados, entorno/versiones, duración y exit code.
5. Tests ejecutados/aprobados/fallidos y logs sanitizados; no número de tests escritos como si se hubieran corrido.
6. Matriz de capacidades de la instalación con evidence IDs y fecha.
7. E2E y sus fixtures, fallos negativos y efectos remotos observados.
8. Prohibiciones respetadas: cero action_post/pagos/declaraciones/unlink en MVP.
9. Riesgos residuales y métricas de rendimiento/coste cuando existan; hipótesis si no.
10. Siguiente paso concreto y única decisión que necesita el propietario en ese momento.

No llamar «listo para producción» a una entrega con gates reales pendientes. No instalar en `agente` porque ya haya un SDK. No afirmar que se hicieron gestiones ante Hacienda o bancos. No atribuir al propietario una aprobación que no consta.

---

## 27. Prompt listo para pegar al Codex del laptop

```text
Trabaja en uniscrolliabrain-cloud/agntia-gestoria desde mi laptop Windows/PowerShell.
Lee completo HANDOFF-CODEX-WINDOWS.md y las instrucciones AGENTS.md locales aplicables.
Comprueba main/HEAD/estado antes de editar y no borres cambios existentes.

C01 esta fusionada. C02 contiene auditoria estatica, pins y 38 comprobaciones,
pero su gate de instalacion/API real sigue BLOCKED aunque el avance este en main.
No hay adaptador Odoo funcional implementado todavia.

Continua la campana Odoo 19 Community empezando por reproducir baseline,
verificar Docker Linux local y resolver la relacion entre imagen y SHA.
Prepara un laboratorio aislado con dos DB y bots de fixtures para cerrar
las verificaciones reales pendientes de C02/C03. No saltes gates ni inventes PASS.

Conserva formulas fiscales, revision humana, evidencias, API y tenancy.
No modifiques uniscrolliabrain-cloud/agente, upstream, produccion ni secretos.
No publiques facturas, no action_post, pagos, declaraciones o borrados contables.
No aceptes URL/ORM/context/tenant/approval arbitrarios escritos por un LLM.

Una rama y PR autocontenida por fase con README/EVIDENCE/TESTS/RISKS/decisiones.
Ejecuta las pruebas y anota SHA, comandos y resultados reales.
La orden de dejar el handoff en main no autoriza fusionar todas las futuras PR.
Pregunta solo lo imprescindible y de una en una; sigue con trabajo independiente.

Empieza explicandome brevemente lo que has comprobado del entorno y ejecuta
los pasos autorizados. Si hay un bloqueo, identifica el comando y la causa
sin esconderlo como una capacidad implementada. Mantente trabajando hasta
completar la fase permitida o tener un bloqueo real y documentado.
```

---

## 28. Referencias esenciales y checklist de entrega

### Fuentes propias

- Repositorio: <https://github.com/uniscrolliabrain-cloud/agntia-gestoria>.
- PR #1: <https://github.com/uniscrolliabrain-cloud/agntia-gestoria/pull/1>.
- PR #2: <https://github.com/uniscrolliabrain-cloud/agntia-gestoria/pull/2>.
- `docs/odoo-adapter/` contiene el detalle y evidencia histórica de C01/C02.
- `docs/calculation-engines.md` y `docs/product-scope.md` describen los límites fiscales existentes.
- `docs/dashboard-and-reports.md` describe los indicadores y exportaciones reales.

### Upstream

- Odoo fijado: <https://github.com/odoo/odoo/tree/60657b50d171ddf84ab58717fdee5ac26031065b>.
- Documentación JSON-2: <https://www.odoo.com/documentation/19.0/developer/reference/external_api.html>.
- Fuente documental fijada: <https://github.com/odoo/documentation/blob/67e8ded4a03d7c53be4e2c4d53471678e9e9352e/content/developer/reference/external_api.rst>.
- OCA España: <https://github.com/OCA/l10n-spain>, solo referencia; módulos no instalados.

### Hechos a conservar al relevar

- C01 fusionada por autorización específica.
- C02 auditada estáticamente, guardada en main por autorización específica del handoff; runtime bloqueado.
- 23 unittest y navegador aprobados en CI de las revisiones indicadas.
- 38 comprobaciones estáticas Odoo ejecutadas y aprobadas; cero pruebas Odoo runtime.
- Ningún secreto real ni dato de cliente utilizado.
- Ningún cambio en `agente`, producción o fórmulas fiscales.
- Ninguna factura Odoo creada/publicada, ningún impuesto presentado, ningún pago ejecutado.
- Primer siguiente resultado: laboratorio verificable que cierre la incertidumbre, no una demo fabricada.

**Principio rector:** AgntiaPro gobierna identidad, políticas, SOPs y experiencia; Gestoría verifica el dominio y conserva evidencia; Odoo custodia hechos ERP; el LLM propone y el sistema autoriza mediante reglas comprobables.
