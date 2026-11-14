# Contratación, altas y seguros laborales

Objetivo: generar y validar contratos con la política del sector, registrar la comunicación al SEPE y calcular el coste real de cada alta con los tipos del ejercicio.

## Etapa 10.1 · Motor de contratos

- **Nuevos:** `agntia_gestoria/integrations/rrhh/contracts/engine.py`, `templates/es/*.md.j2`, `validator.py`, `tests/test_rrhh_contracts_engine.py`, `tests/fixtures/rrhh/contracts/*.json`.
- **Tocados:** `integrations/rrhh/contracts.py` (modelos), `routes.py` (`POST .../rrhh/contracts/draft`, `POST .../rrhh/contracts/{id}/validate`), `packs/compiler.py`.
- **Modalidades soportadas:** indefinido, indefinido adscrito a obra (construcción), producción (máximo 6 meses, ampliable a 1 año por convenio, 90 días/año previsibles), sustitución (reserva de puesto, jornada reducida o selección hasta 3 meses), fijo-discontinuo (llamamiento escrito), tiempo parcial con horas complementarias, formación en alternancia (3 meses a 2 años, 65 % y 85 % de jornada) y práctica profesional (6 meses a 1 año, dentro de 3 años del título).
- **Validaciones duras:** prueba máxima según titulación y tamaño de empresa; jornada no superior a la del convenio; retribución no inferior al convenio ni al SMI (1.221 €/mes en 2026); causa de temporalidad explícita; sin contrato formativo para funciones ya desempeñadas más de 6 meses.
- **Salida:** borrador con avisos, hash de contenido y `next_action` (`send_to_sepe`, `review_by_lawyer`, `sign`). El borrador **no es un contrato firmado**.

```python
def draft_contract(request: ContractRequest, policy: CompiledPolicy) -> ContractDraft:
    warnings = check(policy, request)          # prueba, jornada, salario, causa
    if warnings.blocking:
        raise Reject("contract_policy_violation", details=warnings.as_list())
    body = render(template_for(request.kind), request, policy.params)
    return ContractDraft(kind=request.kind, body=body, warnings=warnings.soft,
                         content_hash=digest(body), status="draft_not_signed")
```

## Etapa 10.2 · Comunicación al SEPE y alta

- **Nuevos:** `contracts/sepe.py`, `tests/test_rrhh_sepe.py`, `docs/rrhh/rrhh-sepe.md`.
- **Tocados:** `routes.py` (`POST .../rrhh/contracts/{id}/notify`), `events.py` (evento `contract.signed`).
- **Reglas:** comunicación en **10 días hábiles** desde la firma (art. 8.3 ET y RD 1424/2002); copia básica a la representación en 10 días; información escrita previa al inicio del trabajo, obligatoria desde el 5 de octubre de 2026 (RD 723/2026); el sistema guarda acuse, fecha y justificante, nunca marca "presentado" sin acuse.
- **Tests:** vencimiento del plazo, comunicación duplicada (una sola), falta de acuse durante 30 días (alerta), contrato sin firma que no se comunica.

## Etapa 10.3 · Coste y seguros sociales

- **Nuevos:** `agntia_gestoria/integrations/rrhh/payroll/rates.py`, `cost.py`, `tests/test_rrhh_cost.py`, `docs/rrhh/tipos-cotizacion-2026.json`.
- **Tocados:** `contracts/engine.py` (coste estimado en el borrador), `routes.py` (`GET .../rrhh/contracts/{id}/cost`).
- **Datos versionados de 2026:** contingencias comunes 23,60 % empresa y 4,70 % persona; desempleo 5,50/1,55 indefinido y 6,70/1,60 temporal; FOGASA 0,20 %; formación 0,60/0,10; MEI 0,75/0,15; horas extra 14 % (fuerza mayor) y 28,30 % (resto); base máxima 5.101,20 €; AT/EP **por CNAE y ocupación**, nunca un tipo fijo.
- **Salida:** coste empresa, retención estimada de la persona y aviso de que AT/EP depende de la tarifa aplicable y de que el IRPF no se calcula aquí.
- **Tests:** salario por debajo de base mínima, salario por encima de base máxima, temporal con recargo de desempleo, contrato de menos de 30 días con cotización adicional, ejercicio sin tabla (falla con `rates_not_available`, no con una cifra inventada).

**Criterio de aceptación:** un alta se puede preparar de principio a fin con avisos legales citados, y ninguna cifra de cotización vive fuera de la tabla versionada.
