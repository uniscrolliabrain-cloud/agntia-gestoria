# C04 · Contratos tipados de lectura y staging

Estado: primer corte de C04 para revisión, dependiente del cierre de C02/C03. Incluye DTOs y esquemas. La validación de permisos, la persistencia y el transporte corresponden a fases posteriores.

| Contrato | Uso |
| --- | --- |
| `PublicConnection`, `OdooBinding` | Proyección de conexión autorizada y binding interno separado. Las referencias de endpoint, base y credencial permanecen en el servidor. |
| `CapabilityReport` | Resultado por capacidad con estados explícitos para soporte, ausencia, denegación y falta de evidencia. |
| `SyncCursor`, `SourceRef`, `ExternalObjectLink` | Paginación por fecha/ID y procedencia por conexión, modelo e ID remoto. La pertenencia del cursor y del binding a la empresa se comprueba antes de ejecutar la operación. |
| `ImportedEconomicFact`, `Money` | Evidencia ERP en staging con importe decimal en texto. Conserva el estado ERP y exige revisión local pendiente. |
| `OperationEnvelope`, `ReadResult` | Sobre interno creado por el servidor tras resolver identidad y scope. Comandos de lectura cerrados y resultados discriminados, sin dominios, métodos o contexto ORM libre. |

Los comandos mutables, sus aprobaciones, la previsualización y la reconciliación requieren contratos específicos por operación. El primer corte deja esas operaciones pendientes. Los DTOs no están conectados a la API de Gestoría ni empaquetados en el SDK TypeScript.

## Comprobaciones

- `python -m unittest discover -s tests -v` ejecuta la suite y los casos de contratos.
- `python -m scripts.export_odoo_contracts` emite los esquemas JSON del primer corte desde la raíz del repo. Las referencias de credenciales y el binding interno quedan fuera de la exportación.
- Prueba local del 10 de noviembre de 2026: 28 pruebas Python aprobadas y serialización de un sobre y un hecho económico mediante Python → JSON Node → Python con conservación de `"100.10"`. La prueba de serialización acredita el formato JSON, con el consumo tipado desde el SDK pendiente.
