import json
from pathlib import Path

import pytest

from agntia_gestoria.integrations.errors import IntegrationError
from agntia_gestoria.integrations.rrhh import packs

HERE = Path(__file__).parent / 'fixtures' / 'rrhh' / 'packs'


def body(**overrides):
    base = json.loads((HERE / 'hosteleria.json').read_text(encoding='utf-8'))
    base.update(overrides)
    return base


def test_pack_compiles_with_its_legal_references():
    policy = packs.compile_policy(packs.load(body()))
    assert policy.sector_id == 'hosteleria'
    assert policy.params['vacaciones_dias_naturales'] == 30
    assert all(rule['base_legal'] for rule in policy.rules)


def test_rule_without_legal_basis_is_rejected():
    data = body()
    data['reglas'][0].pop('base_legal')
    with pytest.raises(ValueError):
        packs.load(data)


def test_pack_cannot_lower_the_legal_floor():
    data = body(politica={'vacaciones_dias_naturales': 22, 'jornada_semanal_horas_max': 40})
    with pytest.raises(IntegrationError) as error:
        packs.compile_policy(packs.load(data))
    assert error.value.code == 'policy_violation'
    assert error.value.status == 422


def test_company_override_cannot_worsen_the_floor():
    policy = packs.load(body())
    with pytest.raises(IntegrationError):
        packs.compile_policy(policy, overrides={'jornada_semanal_horas_max': 45})


def test_two_sectors_compile_independently():
    hosteleria = packs.compile_policy(packs.load(body()))
    comercio = packs.compile_policy(packs.load(body(sector_id='comercio', version='2026.2')))
    assert hosteleria.sha256 != comercio.sha256


def test_hash_is_stable_for_the_same_policy():
    first = packs.compile_policy(packs.load(body()))
    second = packs.compile_policy(packs.load(body()))
    assert first.sha256 == second.sha256


def test_unknown_predicate_is_rejected():
    data = body()
    data['reglas'][0]['cuando'] = {'regex': '.*'}
    with pytest.raises(ValueError):
        packs.load(data)


def test_evaluate_explains_each_rule():
    policy = packs.compile_policy(packs.load(body()))
    hits = packs.evaluate(policy, {'tipo': 'empleado'}, 'tipo')
    assert [hit['rule_id'] for hit in hits] == ['vacaciones.minimo']
    assert hits[0]['base_legal'] == 'art. 38.1 ET'


def test_legal_floor_direction_is_respected():
    from agntia_gestoria.integrations.rrhh import legal_floor
    assert legal_floor.worse_than_floor('vacaciones_dias_naturales', 29) is True
    assert legal_floor.worse_than_floor('vacaciones_dias_naturales', 31) is False
    assert legal_floor.worse_than_floor('jornada_semanal_horas_max', 45) is True
    assert legal_floor.worse_than_floor('jornada_semanal_horas_max', 37.5) is False
