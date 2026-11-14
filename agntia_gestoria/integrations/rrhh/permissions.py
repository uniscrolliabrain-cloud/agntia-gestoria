"""Matriz de permisos: rol × capacidad × superficie.

La misma capacidad puede estar permitida por API y no por SDK, o al contrario.
Cualquier capacidad que no esté explícitamente concedida se deniega: no hay
comodines por nombre, avatar ni parecido.
"""
SURFACES = ('api', 'sdk', 'worker', 'voice')

MATRIX = {
    'owner': {'api': '*', 'sdk': '*', 'worker': '*', 'voice': '*'},
    'reviewer': {
        'api': {'rrhh.read', 'rrhh.closure.prepare', 'rrhh.closure.approve',
                'rrhh.closure.export', 'rrhh.audit.read'},
        'sdk': {'rrhh.read', 'rrhh.closure.prepare'},
        'worker': set(),
        'voice': {'rrhh.read'},
    },
    'viewer': {'api': {'rrhh.read'}, 'sdk': {'rrhh.read'}, 'worker': set(),
               'voice': {'rrhh.read'}},
    'agent': {'api': {'rrhh.read', 'rrhh.closure.prepare'}, 'sdk': {'rrhh.read'},
              'worker': set(), 'voice': {'rrhh.read'}},
}

SENSITIVE = {'rrhh.closure.approve', 'rrhh.closure.export', 'rrhh.payroll.export'}


def allowed(role, capability, surface):
    if surface not in SURFACES:
        return False
    granted = MATRIX.get(role, {}).get(surface, set())
    if granted == '*':
        return True
    return capability in granted


def check(role, capability, surface):
    """Devuelve True o explica la denegación; nunca concede por defecto."""
    if allowed(role, capability, surface):
        return True
    return {'allowed': False, 'role': role, 'capability': capability, 'surface': surface,
            'reason': 'La capacidad no está concedida a este rol en esta superficie'}


def decrement_in_flight(role, capability, surface):
    """Una baja de permisos en mitad de la tarea se comprueba antes del efecto."""
    return allowed(role, capability, surface)


def sensitive(capability):
    return capability in SENSITIVE


def matrix_snapshot():
    return {role: {surface: ('*' if granted == '*' else sorted(granted))
                   for surface, granted in surfaces.items()}
            for role, surfaces in MATRIX.items()}
