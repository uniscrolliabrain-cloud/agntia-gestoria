# Dashboard, datos e informes

## Gestión del dato

- Registro estructurado por empresa: fecha, ingreso/gasto, referencia externa, contraparte, categoría, impuesto, base, cuota, retención, importes deducibles y documentos de soporte.
- Importación CSV con vista previa y validación; el lote JSON posterior se guarda en una transacción. Una referencia duplicada aborta todo el lote. La vista previa no guarda filas ni importa parcialmente las válidas.
- Los documentos y registros quedan separados: el original es la evidencia; la clasificación y los importes son datos revisables. Los agentes no obtienen permiso de revisión humana.
- Anulación conservando el registro original, permisos por empresa, revisiones y auditoría. No se mezclan empresas en informes o exportaciones.

CSV: UTF-8, separador coma, fecha ISO, punto decimal y nombres de campo de la API. Mínimo `external_id,operation_date,kind,description,tax_kind,base_amount,tax_amount`. Para los motores completar categoría, tratamiento, tipo, deducibilidad y documentos. `document_ids` acepta varios IDs separados por `|`. Límite 2.000 filas y 5 MB; las clasificaciones importadas quedan pendientes de revisión. Los negativos no son automáticamente errores; pueden ser rectificaciones, aunque los motores iniciales los excluyen.

## Análisis explicable

El dashboard filtra por ejercicio y muestra ingresos, gastos, diferencia operativa, evolución mensual interactiva, composición de gastos, estado de documentación y cálculos guardados. Incluye datos pendientes de revisión, con su recuento visible. Los ajustes ajenos a ingresos/gastos no se convierten automáticamente en resultado.

Reglas de hallazgos:

- Posibles duplicados: misma fecha, clase, base, cuota y contraparte normalizada. Es una propuesta de comprobación, no una eliminación.
- Falta de justificantes y registros no revisados.
- Gasto atípico: más de tres veces la mediana de gastos positivos, con al menos cinco observaciones.
- Concentración: una contraparte identificada supera el 50% de ingresos registrados.
- Caída de ingresos: más de 20% entre los dos últimos meses con registros. Advierte sobre meses incompletos; no hace previsiones.
- Cálculos basados en datos anteriores.

No se envían documentos ni datos a servicios externos de IA. Estos hallazgos son reglas estadísticas explícitas. Las cifras vienen del registro, no de texto generado.

## Reportes y presentaciones

Generar un informe guarda una versión con datos, métricas, hallazgos, referencias de registros, fecha y huellas. Los cambios posteriores de datos, expedientes o cálculos se señalan sin reescribir la versión guardada.

Exportaciones: PDF con métricas y tabla mensual; PowerPoint con gráfico editable, resumen, gastos, hallazgos y cálculos; SVG de la infografía; HTML autocontenido para compartir o imprimir. Los archivos se generan localmente, respetan el ámbito de empresa y se descargan como adjuntos. Protege el acceso a las copias exportadas: pueden contener información empresarial.

`GET /api/companies/{id}/dashboard?year=2026`, `POST/GET .../reports`, `GET .../reports/{report}/download/{pdf|pptx|svg|html}`. También disponibles para agentes mediante el cliente TypeScript. Los adaptadores Hono conservan consultas y las descargas se hacen desde el backend autorizado.

Los indicadores no equivalen a contabilidad oficial, cuota tributaria global, cobros/pagos ni previsión de caja. No se carga una empresa de ejemplo en los datos del usuario; los archivos demo entregados se generan por separado.
