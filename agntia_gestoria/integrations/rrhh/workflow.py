"""Máquina de estados del cierre.

Cada transición exige actor, motivo y evidencia; algunas exigen además un rol
concreto. El resultado dice qué se puede hacer después, para que la interfaz no
tenga que adivinarlo ni el agente inventarlo.
"""
from ..errors import reject

STATES = ('prepared', 'blocked', 'pending_review', 'approved', 'exported',
          'reconciliation_required')

TRANSITIONS = {
    'prepared': {'blocked': ('owner', 'reviewer'), 'pending_review': ('owner', 'reviewer')},
    'blocked': {'prepared': ('owner', 'reviewer')},
    'pending_review': {'approved': ('owner', 'reviewer'), 'prepared': ('owner', 'reviewer')},
    'approved': {'exported': ('owner', 'reviewer'), 'pending_review': ('owner', 'reviewer')},
    'exported': {'reconciliation_required': ('owner',)},
    'reconciliation_required': {'exported': ('owner',)},
}

NEXT = {
    'prepared': ['pending_review', 'blocked'],
    'blocked': ['prepared'],
    'pending_review': ['approved', 'prepared'],
    'approved': ['exported'],
    'exported': ['reconciliation_required'],
    'reconciliation_required': ['exported'],
}


def apply(current, target, actor, *, reason, evidence):
    if current not in TRANSITIONS:
        reject('invalid_state', f'Estado de origen desconocido: {current}', 422)
    allowed = TRANSITIONS[current]
    if target not in allowed:
        reject('invalid_transition', f'No se puede pasar de {current} a {target}', 409)
    if actor.role not in allowed[target]:
        reject('forbidden', 'Tu rol no permite esa transición', 403)
    if not reason or len(str(reason).strip()) < 5:
        reject('reason_required', 'La transición necesita un motivo', 422)
    if not evidence:
        reject('evidence_required', 'La transición necesita evidencia', 422)
    return {'from': current, 'to': target, 'actor_id': actor.id, 'actor_role': actor.role,
            'reason': str(reason).strip(), 'evidence': evidence,
            'next': NEXT[target]}


def describe(state):
    if state not in NEXT:
        reject('invalid_state', f'Estado desconocido: {state}', 422)
    return {'state': state, 'next': NEXT[state], 'terminal': state == 'exported'}
