# Requisito del producto: gestoría de pymes y autónomos en toda España

Solicitud del titular: procesar y conservar los datos de la empresa y gestionar renta, IVA e IRPF trimestrales/anuales, con el alcance de una gestoría de pymes y autónomos. Se incorpora como objetivo, no como declaración de que estas capacidades ya están terminadas.

## Servicios que debe completar el producto

| Área | Objetivo | Entrega actual | Trabajo pendiente |
| --- | --- | --- | --- |
| Datos | Empresas, actividades, socios/titulares, documentos, facturas, gastos, bancos y personal | Empresas, documentos, expedientes, registro económico estructurado | OCR con confirmación, importadores, conciliación bancaria, inmovilizado, contactos, deduplicación semántica |
| IVA | 303, 390 cuando corresponda, 349 y regímenes especiales | Motor 303 acotado a régimen general interior común 2026, con cuotas corrientes íntegramente deducibles; preparación documental para otros casos | Motor de casillas por ejercicio, prorrata, regularizaciones, criterio de caja, intracomunitarias, importaciones, OSS y validadores oficiales |
| IRPF trimestral | 130 y 131 según régimen, retenciones 111/115 y anuales 190/180 | Motor 130 en directa normal no agraria, común 2026, con acumulados y minoración; preparación documental para otros casos | Directa simplificada/módulos, otras reducciones, regímenes especiales, modelos de retenciones y casos exentos |
| Renta anual | 100 del titular persona física | Expediente y recogida documental | Datos personales y familiares, rentas de todas las fuentes, escalas estatales/autonómicas, patrimonio cuando corresponda, deducciones y opciones conjuntas/individuales |
| Sociedades | 200/202, cierre y cuentas anuales | Calendario nominal y borradores contables | Liquidación, ajustes, amortizaciones, bases negativas, reservas y presentación de cuentas |
| Territorios | Reglas estatales, autonómicas, forales, IGIC e IPSI | Perfiles múltiples y fuentes territoriales | Versiones, modelos y calendarios de cada administración; TicketBAI y demás requisitos según ámbito |
| Laboral | Contratos, nóminas, cotizaciones, altas/bajas y autónomos | Expedientes documentales | Convenios, motor laboral, Sistema RED y conectores autorizados |
| Representación | Preparación, revisión, presentación, justificante y rectificaciones | Preparación interna con permisos y trazabilidad | Apoderamientos, certificados, colaboración social, conectores oficiales y conciliación de justificantes |

## Condiciones para habilitar una declaración

1. Identificar contribuyente, ejercicio, período, régimen, administración y normativa aplicable. La renta personal no se obtiene solo de las facturas de una empresa.
2. Completar datos y documentos y revisar clasificaciones. El texto extraído por IA es una propuesta; los importes y casillas se calculan mediante reglas deterministas verificadas.
3. Usar reglas y formatos versionados para el ejercicio y territorio, con pruebas de casos normales, límites y excepciones contrastadas con fuentes oficiales.
4. Permitir revisar casillas y evidencias. Toda modificación conserva una revisión nueva y deja obsoletas las preparaciones basadas en datos anteriores.
5. Obtener representación y credenciales válidas para el trámite. Un expediente aprobado no acredita presentación.
6. Considerar presentada una declaración solo con respuesta aceptada y justificante auténtico de la administración. Conservar rectificaciones y complementarias sin borrar su historia.

Las preparaciones documentales genéricas incluyen resúmenes aritméticos de registros declarados por el usuario; no calculan cuota, resultado ni fichero oficial. Los modelos sin motor legal validado quedan bloqueados para presentación. Las integraciones oficiales se habilitarán por modelo, ejercicio y territorio, nunca mediante una promesa universal de conformidad.

## Conservación y seguridad de datos

El almacenamiento actual es SQLite con documentos en disco, permisos por empresa y registro de acciones. No cifra automáticamente archivos ni base de datos: en producción hacen falta disco cifrado, HTTPS, secretos protegidos, copias de seguridad cifradas y pruebas de restauración. Establecer una política de conservación por clase documental y sus obligaciones; no borrar todo al prescribir un impuesto. El exportador actual exporta datos y metadatos, no sustituye una copia de los originales.

## Fuentes específicas consultadas el 09/11/2026

- [AEAT: pagos fraccionados 130/131](https://sede.agenciatributaria.gob.es/Sede/irpf/retenciones-ingresos-cuenta-pagos-fraccionados/pagos-fraccionados.html): régimen y excepciones, no una obligación universal.
- [AEAT: instrucciones 303 de 2026](https://sede.agenciatributaria.gob.es/Sede/todas-gestiones/impuestos-tasas/iva/modelo-303-iva-autoliquidacion_/instrucciones-2026/instrucciones-02-12-2t-4t-2026.html): casillas, períodos y condiciones, incluida la exoneración del resumen anual en determinados casos.
- [AEAT: colaboración social](https://sede.agenciatributaria.gob.es/Sede/colaborar-agencia-tributaria/colaboracion-social-presentacion-declaraciones/preguntas-frecuentes-sobre-colaboracion-social.html): presentación de terceros, certificados y límites de la representación.

## API de datos y preparación

`POST/GET /api/companies/{id}/tax-records`: ingresos, gastos, retenciones y ajustes, importes decimales en EUR, referencias externas únicas y documentos de la misma empresa. No se deducen tipos, deducibilidad o devengo. Para corregir un registro se anula con revisión y se añade otro con referencia nueva; el original permanece.

`POST /api/companies/{id}/tax-records/{record}/void`: anulación interna controlada por revisión.

`POST/GET /api/companies/{id}/tax-preparations`: captura del período y resumen aritmético por clase de registro/impuesto, con bloqueo explícito de liquidación/presentación. Un cambio posterior del perfil o los registros se indica en `data_changed_since_preparation`. Para 130 este resumen trimestral no sustituye los acumulados exigibles por el modelo. Los importes registrados no se trasladan a casillas oficiales.

Los [motores acotados 303 y 130](calculation-engines.md) son una ruta independiente de las preparaciones genéricas y sí calculan casillas del supuesto admitido. El [dashboard y las exportaciones](dashboard-and-reports.md) transforman los registros en informes y presentaciones sin inventar datos.
