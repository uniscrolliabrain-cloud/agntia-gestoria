"""Paquetes de sector: el sector es dato, el código es genérico.

Un paquete declara ontología, política, reglas y plantillas. Se valida contra los
suelos legales y se compila en una política inmutable con hash, que es lo que
después viaja al snapshot, a la aprobación y a la auditoría.
"""
import json
from dataclasses import dataclass, field

from ...storage import digest
from ..errors import reject
from . import legal_floor

PREDICATES = ('eq', 'in', 'gte', 'lte', 'gt', 'lt', 'between')


@dataclass(frozen=True)
class SectorPack:
    sector_id: str
    version: str
    politica: dict
    reglas: tuple
    ontologia: dict = field(default_factory=dict)
    convenio: dict = field(default_factory=dict)


@dataclass(frozen=True)
class CompiledPolicy:
    sector_id: str
    version: str
    params: dict
    rules: tuple
    legal_floor_version: str
    sha256: str


def parse(text, *, source='pack'):
    try:
        body = json.loads(text)
    except ValueError as exc:
        raise ValueError(f'{source}: JSON inválido') from exc
    return body


def load(body, *, source='pack'):
    if not isinstance(body, dict):
        raise ValueError(f'{source}: se esperaba un objeto')
    for key in ('sector_id', 'version', 'politica', 'reglas'):
        if key not in body:
            raise ValueError(f'{source}: falta {key}')
    if not isinstance(body['politica'], dict):
        raise ValueError(f'{source}: politica debe ser un objeto')
    if not isinstance(body['reglas'], list):
        raise ValueError(f'{source}: reglas debe ser una lista')
    for index, rule in enumerate(body['reglas']):
        if not isinstance(rule, dict) or not rule.get('id'):
            raise ValueError(f'{source}: regla {index} sin id')
        if not rule.get('base_legal'):
            raise ValueError(f'{source}: regla {rule["id"]} sin base_legal')
        when = rule.get('cuando')
        if not isinstance(when, dict) or len(when) != 1:
            raise ValueError(f'{source}: regla {rule["id"]} necesita un único predicado')
        predicate = next(iter(when))
        if predicate not in PREDICATES:
            raise ValueError(f'{source}: regla {rule["id"]} usa un predicado no soportado')
    return SectorPack(body['sector_id'], body['version'], body['politica'],
                      tuple(body['reglas']), body.get('ontologia', {}), body.get('convenio', {}))


def validate(pack):
    """Devuelve la lista de incumplimientos; no lanza para poder explicarlos todos."""
    problems = []
    for key, value in pack.politica.items():
        if key in legal_floor.FLOOR and legal_floor.worse_than_floor(key, value):
            problems.append({'key': key, 'value': value, 'floor': legal_floor.FLOOR[key],
                             'base_legal': legal_floor.reference(key)})
    if not pack.convenio.get('codigo'):
        problems.append({'key': 'convenio.codigo', 'value': None, 'floor': 'trazabilidad',
                         'base_legal': 'art. 85.3 ET'})
    return problems


def compile_policy(pack, *, overrides=None):
    problems = validate(pack)
    if problems:
        reject('policy_violation', 'El paquete de sector incumple un suelo legal', 422)
    params = dict(pack.politica)
    for key, value in (overrides or {}).items():
        if legal_floor.worse_than_floor(key, value):
            reject('policy_violation', f'La empresa no puede empeorar {key}', 422)
        params[key] = value
    payload = {'sector_id': pack.sector_id, 'version': pack.version, 'params': params,
               'rules': list(pack.reglas), 'floor': legal_floor.VERSION}
    return CompiledPolicy(pack.sector_id, pack.version, params, pack.reglas,
                          legal_floor.VERSION, digest(payload))


def accepts(predicate, facts, expected):
    if predicate == 'eq':
        return facts == expected
    if predicate == 'in':
        return facts in expected
    if predicate == 'gte':
        return facts >= expected
    if predicate == 'lte':
        return facts <= expected
    if predicate == 'gt':
        return facts > expected
    if predicate == 'lt':
        return facts < expected
    if predicate == 'between':
        return expected[0] <= facts <= expected[1]
    return False


def evaluate(policy, facts, field_name):
    """Reglas aplicables a un hecho concreto, explicando norma y resultado."""
    result = []
    value = facts.get(field_name)
    for rule in policy.rules:
        when = rule['cuando']
        predicate, expected = next(iter(when.items()))
        if accepts(predicate, value, expected):
            result.append({'rule_id': rule['id'], 'then': rule.get('entonces', {}),
                           'base_legal': rule['base_legal']})
    return result
