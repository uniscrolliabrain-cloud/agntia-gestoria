# C04 · Contratos tipados de lectura, staging y contactos

Estado: primer corte de C04 para revisión, dependiente del cierre de C02/C03. Incluye DTOs y esquemas. La validación de permisos, la persistencia y el transporte corresponden a fases posteriores.

| Contrato | Uso |
| --- | --- |
| `PublicConnection`, `OdooBinding` | Proyección de conexión autorizada y binding interno separado. Las referencias de endpoint, base y credencial permanecen en el servidor. |
| `CapabilityReport` | Resultado por capacidad con estados explícitos para soporte, ausencia, denegación y falta de evidencia. |
| `SyncCursor`, `SourceRef`, `ExternalObjectLink` | Paginación por fecha/ID y procedencia por conexión, modelo e ID remoto. La pertenencia del cursor y del binding a la empresa se comprueba antes de ejecutar la operación. |
| `ImportedEconomicFact`, `Money` | Evidencia ERP en staging con importe decimal en texto. Conserva el estado ERP y exige revisión local pendiente. |
| `OperationEnvelope`, `ReadResult` | Sobre interno creado por el servidor tras resolver identidad y scope. Comandos de lectura cerrados y resultados discriminados, sin dominios, métodos o contexto ORM libre. |
| `ContactPreviewRequest`, `ContactPreview`, `ApprovedContactWrite` | Candidato editable separado de la ejecución interna, que referencia una previsualización persistida y su hash, la aprobación humana y la clave idempotente. |
| `ContactWriteResult` | Resultado confirmado, rechazo o reconciliación requerida. El resultado incierto carece de ID remoto y de instrucción de reintento. |

El futuro ejecutor debe verificar que la aprobación existe, pertenece al scope correcto, sigue vigente y corresponde al hash de la previsualización. Persistencia, ejecución, reconciliación y contratos para otras mutaciones quedan pendientes. Los DTOs aún no se usan en la API de Gestoría ni en el SDK TypeScript.

## Comprobaciones

- `python -m unittest discover -s tests -v` ejecuta la suite y los casos de contratos.
- `python -m scripts.export_odoo_contracts` emite los esquemas JSON del primer corte desde la raíz del repo. Las referencias de credenciales y el binding interno quedan fuera de la exportación.
- Prueba local del 10 de noviembre de 2026: 30 pruebas Python aprobadas y serialización de un sobre y un hecho económico mediante Python → JSON Node → Python con conservación de `"100.10"`. La prueba de serialización acredita el formato JSON, con el consumo tipado desde el SDK pendiente.
