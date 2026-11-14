# Trazabilidad con la campaña y riesgos

## Correspondencia con la campaña del 11 de noviembre

| Campaña | Plan | Repositorio |
|---|---|---|
| Etapa 0 · Descubrimiento | Fase 1 · etapa 1 (matriz de fuentes y bandera) | ambos |
| Etapa 1 · Scaffolding y laboratorio | Fases 1.1 a 1.3 y 3.1 | agntia-gestoria |
| Etapa 2 · Motor determinista | Fase 2 completa | agntia-gestoria |
| Etapa 3 · Herramientas y evaluaciones | Fase 4 (contrato) y evaluaciones en `agente` | agntia-gestoria + agente |
| Etapa 4 · Anam y portal | Fuera de este plan | agente |
| Etapa 5 · Ampliación por módulos | Fase 5 (olas 1 a 3) | ambos |
| Etapa 6 · Hardening y operación | Fase 6 completa | ambos |

## Orden de ejecución

1. Fase 1 completa (bloquea todo lo demás: sin aislamiento y sin contratos no se expone dato laboral).
2. Fase 2 completa (primer resultado verificable: cierre de octubre sintético).
3. Fase 3 en paralelo con la 2 sólo desde la etapa 3.1 (laboratorio), nunca antes de cerrar 2.2.
4. Fase 4 después de 2.3: el runtime no debe consumir capacidades sin aprobación probada.
5. Fase 5 por olas: ausencias y turnos, después incorporación, después nómina.
6. Fase 6 antes de cualquier piloto con datos reales.

## Riesgos y mitigación

| Riesgo | Mitigación |
|---|---|
| Base equivocada: `main` no tiene el adaptador | Ramas desde `verify/odoo-complete-adapter`, SHA declarado en cada PR |
| Permiso implícito desde loopback | Cerrar SEC-01 en la etapa 1.1, antes de exponer el módulo |
| Upsert que cruza empresas | Helpers de escritura con `company_id` y `unique_key` en la etapa 1.2 |
| Doble efecto en exportación | Clave idempotente y reconciliación antes del efecto |
| Addon ausente en Odoo | Capacidad declarada no disponible y degradación probada |
| Laboratorio inexistente en el entorno actual | Etapas 3.x y las medidas de 6.2 quedan BLOCKED hasta tener Docker y Odoo 19 |
| Contrato cambiado desde dos repos | Publicar esquema y fixtures antes del consumidor; fijar revisión |

## Qué NO incluye este plan

Selección, desempeño, formación, gastos, informes de gestión, portal, Anam, conversación, SOPs, scheduler y evaluaciones del agente. Todo eso es de `agente` o de olas posteriores.

## Estado de esta revisión

Nada implementado. Este documento propone ficheros, pruebas, cableado y código; la aprobación de la base (`verify/odoo-complete-adapter`) y del orden de fases es la decisión pendiente antes de empezar.
