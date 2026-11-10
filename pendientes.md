# Pendientes · entrega Freebuff del 11 de noviembre de 2026

Rama `freebuff/gestoria-autonomo` (base `b34b8ca`). Todo lo que sigue **no** está cerrado. Se agrupa por motivo, con el primer paso concreto para retomarlo. El detalle por punto está en `docs/odoo-adapter/freebuff-delivery-2026-11-11.md`.

## 1 · No se puede ejecutar en este entorno (sin Docker, sin Odoo 19, sin PostgreSQL)

Estos puntos necesitan laboratorio real. Ninguno se ha simulado como si lo fuera.

| Punto | Qué falta | Primer paso |
|---|---|---|
| 02 | Smoke completo en dos bases A y B con volúmenes nuevos | `scripts/odoo_bootstrap.py` sobre volúmenes limpios y registrar conteos y auditoría |
| 03 | Suite A–E real | `AGNTIA_RUN_ODOO_TESTS=1 python -m pytest tests/integration -q` con `AGNTIA_LAB_STATE_DIR` y marcador sintético |
| 05 | Backup y restauración con PostgreSQL y filestore | `scripts/odoo_backup.py` + restore a base nueva y comparación de hashes |
| 06 | Bridge sin addon contable | Variante de laboratorio con `base`, `contacts` y bridge base |
| 07 | Caducidad y revocación de credencial real | Emitir credencial sintética, leer, revocar y repetir |
| 08 | Procedencia del build | Registrar SHA de código, imagen, Odoo, PostgreSQL, módulos y marcador |
| 09 | Aprovisionamiento interrumpido | Arrancar desde cero y cortar una instalación sintética |
| 28 | Contención de incertidumbre en el runtime de Agente | Harness de la PR #12 sobre `b37b67d4e18987402d255d377343a3454d723e5e` |
| 30, 32, 34, 37, 38 | Simulación de extremo a extremo, dos tenants, caídas y ACK perdido real | Runtime desechable + Odoo real; §29–39 del handoff |
| 31, 33 | Sesión autenticada real y catálogo de herramientas | Runtime de Agente con identidad de host |
| 35 | Odoo caído con Gestoría disponible | Cortar acceso al proveedor en laboratorio |
| 39, 70, 71 | Incorporación mínima, piloto de lectura y primer contacto aprobado | Decisión del propietario y checklist de reversión |
| 40–52 (partes reales) | Matriz de facturas, líneas técnicas, adjuntos y restauración | Fixtures de laboratorio por caso |
| 43, 44, 54, 61 | Fallo a mitad de guardado, archivado/borrado real, cursor expirado, obsolescencia con datos reales | Inyección de fallos en laboratorio |
| 63, 66, 67, 68, 69 | Cargas p50/p95, dos procesos, restore completo, reversión con cola y simulacros | Laboratorio y operación real |
| 46, 47, 52 | Rectificativas, descuentos, impuestos compuestos, rotación de adjuntos | Fixtures nuevos antes de tocar código |

## 2 · Requiere el runtime de Agente (no disponible aquí)

Puntos 28 a 39 en su mitad real. Sin el checkout de Agente no se puede acreditar ni el catálogo de herramientas (33) ni la identidad del host (31) ni la lectura de extremo a extremo (30). **Las escrituras de Agente siguen bloqueadas** hasta que la prueba de resultado incierto conserve `outcome_unknown` con un solo efecto.

## 3 · Decisiones que no me corresponden

| Punto | Decisión pendiente |
|---|---|
| 10 | Correspondencia de esta entrega con las fases C02–C20 de la campaña |
| 11 | Portar el cierre humano de PR #12 (`78ca93b`) a una rama de ensayo, con commit de integración y ambos SHAs anotados |
| 14 | Regla explícita para contactos compartidos (`company_id` vacío). Hoy se rechazan con `scope_violation`; si Gestoría quiere admitirlos, hace falta regla, procedencia y prueba |
| 53 | Reutilizar el outbox `schemaVersion: 1` o extenderlo/versionarlo; falta ADR |
| 58–60, 72–82 | Producto e interfaz: vista, bandeja, informes, compras, banca, conservación y demo repetible |
| 79, 81 | Fronteras preparación/emisión/presentación y política de conservación y baja (requiere revisión experta y legal) |

## 4 · No verificado por falta de alcance en esta pasada

- **29**: empaquetar el SDK y consumirlo en un proyecto temporal con las versiones de Node y Hono del host.
- **55 (mitad TypeScript)**: validar los ejemplos TypeScript contra `docs/odoo-adapter/schemas/contracts-v1.json`; hoy el test de deriva solo cubre Python.
- **12 (resto de la matriz)**: adjuntos, exportación y resolución de conflictos por rol.
- **20 (artefactos de CI)**: la búsqueda de centinelas cubre respuestas y auditoría, no los logs ni artefactos de un workflow.

## 5 · Cosas que se intentaron y se dejaron

Ninguna. Los fallos de esta pasada fueron de las propias pruebas y se corrigieron en el momento (métricas sin columna `operation`, regla real de multiempresa en el registro, actor correcto en el test concurrente y forma del cuerpo de error en la prueba de permisos). No hay ningún punto abandonado tras tres intentos.

## 6 · Riesgos abiertos que conviene mirar primero

1. **Sin credenciales git en el entorno**: la rama se publica a través de la integración de GitHub, no con `git push`. Si el flujo cambia, hay que confirmar que la rama remota sigue coincidiendo con el clon.
2. **`IntegrationError.public()`** añade dos campos. Es aditivo, pero cualquier consumidor que compare el conjunto exacto de claves debe actualizarse.
3. **Retención de claves en 42 días** es una propuesta, no una aprobación: si la restauración tolerada crece, la ventana y su ADR también.
