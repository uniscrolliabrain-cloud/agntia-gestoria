# Matriz de capacidades · fuentes frente a instalación

Fecha: 09/11/2026. Todos los estados de instalación son **unknown / NOT VERIFIED**; ninguna capacidad queda habilitada. `supported_by_source` solo describe la presencia del contrato en el upstream fijado, no una prueba de ejecución ni un permiso del bot.

| Capacidad prevista | Evidencia estática | Instancia real | Habilitada |
| --- | --- | --- | --- |
| Transporte JSON-2 bearer | supported_by_source: handler y documentación | unknown | No |
| res.company read y binding | Modelo esperado del core; ACL efectiva pendiente | unknown | No |
| res.partner search_read | Campos en core y ejemplo oficial; reglas permiten compartidos | unknown | No |
| res.partner create/update | CRUD estándar previsto; dry-run/aprobación/idempotencia no implementados | unknown | No |
| account.move search_read | Modelo y campos presentes en account | unknown | No |
| account.move.line read | Campos y display_type presentes; mapping no implementado | unknown | No |
| account.tax read | Modelo, compañía y composición presentes | unknown | No |
| account.account read | company_ids plural verificado | unknown | No |
| account.journal read | Referenciado por movimientos y ACL; discovery concreto pendiente | unknown | No |
| res.currency read | Referenciado por campos de moneda; permisos efectivos pendientes | unknown | No |
| ir.attachment metadatos/descarga | No ensayado ni mapeado en esta fase | unknown | No |
| ir.module.module diagnóstico | No ensayado con bot mínimo | unknown | No |
| Crear factura draft atómicamente | Contrato ORM existe; garantías transaccionales de negocio aún no probadas | unknown | No |
| Publicar, enviar email, pagar, conciliar o eliminar | Prohibido por mandato, aunque Odoo exponga métodos | unsupported_by_policy | No |
| Presentación fiscal oficial | No implementada en Gestoría ni demostrada por addons | unsupported_by_policy | No |

## Jurisdicciones

| Jurisdicción | Observado en fuentes | Automatización fiscal del adaptador |
| --- | --- | --- |
| Territorio común | account y l10n_es en Community; datos de informes españoles | No habilitada; mantiene únicamente los motores acotados existentes de Gestoría. |
| Canarias | Manifiesto l10n_es lista mod420 | unknown; no convertir automáticamente impuesto en IVA/IGIC ni afirmar cobertura funcional. |
| Álava, Bizkaia, Gipuzkoa, Navarra | No se han verificado módulos territoriales concretos | unknown; deshabilitada. |
| Ceuta/Melilla | No se han verificado módulos/ordenanzas aplicables | unknown; deshabilitada. |
| OCA | No instalado ni auditado por módulos en esta fase | unknown; no seleccionar addons en bloque. |

No se han ejecutado fields_get, search_read, tests de ACL, creación de borradores, dos DB o pruebas negativas sin account. Las 38 comprobaciones de fuente no cambian estos estados. El gate integral de C02 continúa BLOCKED por verificación de instalación pendiente.
