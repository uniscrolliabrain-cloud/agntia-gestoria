# Investigación normativa inicial

Fecha de consulta: 2026-11-09. El catálogo legible por máquina está en `agntia_gestoria/data/legal_sources.json`. Cada propuesta conserva identificadores de fuente y versión del catálogo; una aprobación identifica al revisor. Las fuentes deben actualizarse antes de usar propuestas para un ejercicio posterior. El mapa es inicial y depende de territorio, actividad y hechos de cada empresa.

| Área | Fuentes y efectos concretos |
| --- | --- |
| Sociedades | [LSC](https://www.boe.es/buscar/act.php?id=BOE-A-2010-10544), arts. 164, 253 y 279: formulación en tres meses, junta ordinaria en seis y depósito un mes después de la aprobación efectiva. |
| Libros y conservación | [Código de Comercio](https://www.boe.es/buscar/act.php?id=BOE-A-1885-6627), arts. 27 y 30: legalización en cuatro meses y conservación seis años desde el último asiento, sin excluir otros plazos. |
| Fiscalidad | [LGT](https://www.boe.es/buscar/act.php?id=BOE-A-2003-23186), leyes de IVA, IRPF e IS y reglamento censal. La prescripción general de cuatro años no autoriza borrar toda documentación al cumplirlos. El art. 124 de IS fija una regla general nominal de presentación: 25 días naturales tras seis meses desde el cierre. |
| Facturación | [RD 1619/2012](https://www.boe.es/buscar/act.php?id=BOE-A-2012-14696), en particular art. 6. La aplicación crea borradores sin numeración fiscal ni emisión. |
| Contabilidad | PGC y PGC PYMES: la elegibilidad y los criterios contables requieren evaluación; un asiento equilibrado no es suficiente. |
| Laboral | LGSS, Estatuto de los Trabajadores y prevención de riesgos: depende de plantilla, socios y administradores. No se infiere automáticamente el encuadramiento de un administrador. |
| Privacidad | RGPD, LOPDGDD y guías AEPD: permisos por empresa, minimización y conservación justificada. El tamaño pequeño no elimina estas obligaciones. |
| Servicios a terceros | [Ley 10/2010](https://www.boe.es/buscar/act.php?id=BOE-A-2010-6737), art. 2.1.m: evaluar obligaciones cuando se actúa profesionalmente como contable externo o asesor fiscal. La gestión interna no equivale a habilitación profesional o representación ante organismos. |

## Dos calendarios distintos de facturación

**SIF/VERI*FACTU:** la [nota de la AEAT sobre la ampliación](https://sede.agenciatributaria.gob.es/Sede/iva/sistemas-informaticos-facturacion-verifactu/nota-informativa-ampliacion-plazo-adaptacion-facturacion.html) recoge adaptación antes del 1 de enero de 2027 para contribuyentes del IS y antes del 1 de julio de 2027 para los demás afectados. Comprobar ámbito, exclusiones y relación con SII. No confundir una propuesta legislativa con una modificación vigente.

**Factura electrónica B2B:** [RD 238/2026](https://www.boe.es/buscar/act.php?id=BOE-A-2026-7295) y [Orden HAC/1028/2026](https://www.boe.es/buscar/act.php?id=BOE-A-2026-20587). La [AEAT explica el cómputo desde el 6 de octubre de 2026](https://sede.agenciatributaria.gob.es/Sede/todas-noticias/2026/octubre/7/solucion-publica-facturacion-electronica.html): primer grupo de volumen superior a ocho millones, 6 de octubre de 2027; resto, emisión/recepción en 2028; comunicación de estados y pagos de personas físicas y entidades en atribución del segundo grupo, 2029. Aplicar solo tras comprobar el ámbito B2B y exclusiones.

Las reglas muestran estas fechas para preparar tareas. No implementan los formatos, registros, firma, remisión ni certificaciones de esos sistemas.

## Siguiente trabajo

Completar los paquetes normativos territoriales y sus reglas por ejercicio; contrastar modelos y calendarios oficiales por ejercicio; diseñar adaptadores administrativos con credenciales delegadas y justificantes. Conservar separados estado interno y presentación real. La cadena hash del registro local sirve para detectar cambios parciales, pero un administrador de la base puede reescribirla: no es una firma ni un archivo inmutable certificado.

## Alcance nacional y varias administraciones

El perfil diferencia domicilio/territorio fiscal de referencia, territorios de actividad y administraciones declaradas para cada impuesto. Puede registrar varias administraciones para un mismo impuesto, sin inferir competencia ni porcentajes de reparto. Estas declaraciones son datos del usuario pendientes de contrastar.

- País Vasco: [Concierto Económico, Ley 12/2002](https://www.boe.es/buscar/act.php?id=BOE-A-2002-9969). Se distinguen Álava/Araba, Bizkaia y Gipuzkoa.
- Navarra: [Convenio Económico, Ley 28/1990](https://www.boe.es/buscar/act.php?id=BOE-A-1990-31117).
- Canarias: [Ley 20/1991](https://www.boe.es/buscar/act.php?id=BOE-A-1991-14463), IGIC y otros elementos del REF, con desarrollo autonómico pendiente de incorporar.
- Ceuta y Melilla: [Ley 8/1991](https://www.boe.es/buscar/act.php?id=BOE-A-1991-7645), IPSI, más ordenanzas y calendarios locales pendientes.

Las reformas de 2025 del Concierto y Convenio modifican umbrales con efectos que dependen del ejercicio. No se ha programado un umbral universal para adjudicar administraciones. Deben evaluarse normativa aplicable, exacción e inspección por separado y por tributo. Operar en Canarias o Ceuta no elimina por sí solo obligaciones estatales; un domicilio foral tampoco basta para descartar tributación conjunta.

Cobertura entregada: registro de perfiles, fuentes y expedientes de comprobación. Pendiente: liquidación fiscal completa, calendarios locales/forales, TicketBAI y sistemas relacionados según territorio, y presentación ante las administraciones correspondientes.
