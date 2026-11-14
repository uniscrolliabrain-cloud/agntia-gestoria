# Flow específico — agntia-gestoria

reconciliar auditoría histórica con fixes y SHA de main → reproducir CI y laboratorio sintético → clasificar 92 hallazgos por corregido/parcial/pendiente/no reproducido → cerrar gaps críticos → identidad Supabase/twins/tenant → límites fiscales y Odoo → evidencias live, backups y restauración → integración padre → piloto acotado → aceptación founder

**Gates de etapa:** BASELINE_OBSERVED → ASTRA_META_AUDIT_PENDING → FINDINGS_RECONCILED → CAMPAIGN_DELTA_APPROVED → FREEBUFF_IMPLEMENTATION → CODEX_SHA_VERIFICATION → ARCHITECT_REVIEW → FOUNDER_APPROVAL → RELEASE. No transformar documentación en PASS. Futuros handoffs por campaña deben enumerar superficies de escritura, patchsets, dependencias, acceptance, evidencia, rollback y condiciones BLOCKED.

## Reglas de ejecución
Sin modificación de main, padre ni despliegue por defecto. Ramas por campaña, escritor único, pruebas independientes sobre SHA congelado, no ocultar fallos. Diferenciar smoke sintético, integración real y aceptación de cliente. Los resultados previos son históricos hasta reproducirlos.
