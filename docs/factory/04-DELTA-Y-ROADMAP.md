# Del estado actual a terminado — agntia-gestoria

## Baseline conocido
Servicio Python/FastAPI+SQLite y SDK TS existente; motores 303/130, expedientes, informes y adaptador Odoo Community con C01–C20, evidencia local y laboratorio real sintético según docs/odoo-adapter/freebuff-operational-2026-11-11.md. PR #13 descrita como integrada en main. No extrapolar pruebas sintéticas a producción, fiscalidad universal ni piloto aprobado.

## Ruta de finalización
reconciliar auditoría histórica con fixes y SHA de main → reproducir CI y laboratorio sintético → clasificar 92 hallazgos por corregido/parcial/pendiente/no reproducido → cerrar gaps críticos → identidad Supabase/twins/tenant → límites fiscales y Odoo → evidencias live, backups y restauración → integración padre → piloto acotado → aceptación founder

## Riesgos y límites
No publicar facturas ni asientos, pagar, conciliar, presentar impuestos ni auto-review. IVA/IGIC/territorios con fuentes y humano. Odoo Community como backend invisible; no sustituir UI. No asumir que auditoría 11-11 sigue vigente tras fixes ni que laboratorio sintético equivale producción.

## No resuelto
Reproducibilidad del HEAD, compatibilidad real con padre, requisitos por tenant, costos, despliegue, aceptación y licencias/privacidad. Los documentos de campaña son **plan**, no evidencia de ejecución. Astra puede cuestionar este roadmap libremente.
