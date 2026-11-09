# Motores de cálculo y ámbito admitido

Versión inicial `aeat-common-2026-v1`, instrucciones consultadas el 09/11/2026. Son motores deterministas que calculan casillas, no una IA que estima porcentajes. Los datos, la solicitud, las fórmulas, las fuentes y una huella de contenido se conservan con cada resultado. Todos los importes usan Decimal y redondeo monetario HALF_UP.

## Modelo 303, ejercicio 2026, trimestres 1T a 4T

Tributación exclusiva ante AEAT; régimen general con operaciones interiores corrientes al 4%, 10% y 21%. Gastos con IVA íntegramente deducible. Los gastos ordinarios expresamente clasificados como sin IVA, con cuota y deducción cero, se identifican en `excluded_from_boxes` y no se trasladan al 303. Calcula bases y cuotas por tipo, IVA devengado, deducible, diferencia, compensación anterior aplicada y saldo pendiente. Conserva separados el saldo anterior no consumido y el negativo generado en el período. No solicita devolución ni presume que un resultado esté pagado.

Fuentes: [instrucciones 1T](https://sede.agenciatributaria.gob.es/Sede/todas-gestiones/impuestos-tasas/iva/modelo-303-iva-autoliquidacion_/instrucciones-2026.html) e [instrucciones 2T–4T](https://sede.agenciatributaria.gob.es/Sede/todas-gestiones/impuestos-tasas/iva/modelo-303-iva-autoliquidacion_/instrucciones-2026/instrucciones-02-12-2t-4t-2026.html).

No admite prorrata ni deducción parcial, bienes de inversión, recargos, importaciones, operaciones intracomunitarias, inversión de sujeto pasivo, criterio de caja, regímenes especiales, tributación conjunta, rectificativas ni situaciones concursales. El usuario debe confirmar que no existen circunstancias excluidas ni operaciones omitidas. Los libros deben estar completos: un registro ausente no puede detectarse únicamente con el registro existente.

## Modelo 130, ejercicio 2026, trimestres 1T a 4T

Persona física con modelo 130 confirmado, estimación directa **normal**, actividades no agrarias ordinarias, sin deducción Ceuta/Melilla/La Palma, rendimientos irregulares, deducción de vivienda, 131 simultáneo ni complementaria. Calcula ingresos, gastos fiscalmente deducibles y retenciones acumulados desde enero, el 20% del rendimiento positivo, las casillas previas declaradas, la minoración por rendimiento del año anterior y negativos pendientes aplicables.

[Instrucciones oficiales](https://sede.agenciatributaria.gob.es/Sede/impuestos-tasas/impuesto-sobre-renta-personas-fisicas/modelo-130-irpf______esionales-estimacion-directa-fraccionado_/instrucciones.html).

La casilla 05 usa la suma de casillas 07 positivas anteriores; no se sustituye por lo pagado en banco. Se excluye vivienda, por lo que las casillas 16 anteriores deben ser cero en este supuesto. La casilla 12 no baja de cero; la minoración de 13 puede producir un 14/19 negativo. Los negativos previos se limitan al positivo de 14. No se determina automáticamente si un gasto es deducible ni se calculan amortizaciones. Estas deben estar incorporadas, cuando proceda, en el libro fiscal completo y revisado, con su soporte y clasificación; la primera versión no automatiza ese proceso.

## Controles de entrada

Cada registro utilizado debe tener documento vinculado, clasificación admitida y revisión por owner/reviewer. Un agente puede importar, proponer y calcular, pero no aprobar un registro. Una clasificación fuera de ámbito bloquea el cálculo completo; no se omiten filas silenciosamente. Los registros se corrigen anulando y creando una referencia nueva para conservar la historia. Todo cambio del perfil o libro marca los cálculos previos como basados en datos anteriores.

`POST /api/companies/{id}/tax-calculations` recibe `model`, `year`, `period`, `regime`, `confirmed_standard_scope` y los saldos previos aplicables. `GET` permite consultarlos. No existe un endpoint de presentación oficial. No se calcula renta anual completa, módulos, IS, IGIC, IPSI ni liquidación foral en esta versión.
