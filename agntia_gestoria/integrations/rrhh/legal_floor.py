"""Suelos legales del Estatuto, versionados por fecha.

Ningún paquete de sector puede dejar a una persona por debajo de estos valores.
Los números viven aquí y en ningún otro sitio: si cambia la norma, se añade una
versión nueva con su fecha y su referencia, y el hash de la política cambia.
"""

VERSION = '2026-11'

FLOOR = {
    'vacaciones_dias_naturales': 30,
    'jornada_semanal_horas_max': 40,
    'jornada_diaria_horas_max': 9,
    'descanso_entre_jornadas_horas': 12,
    'horas_extra_anuales_max': 80,
    'prueba_meses_tecnico_titulado_max': 6,
    'prueba_meses_resto_max': 2,
    'prueba_meses_menos_25_max': 3,
    'preaviso_dias_objetivo': 15,
    'preaviso_dias_colectivo': 30,
    'nocturnidad_inicio': '22:00',
    'nocturnidad_fin': '06:00',
    'semanas_nocturnas_consecutivas_max': 2,
    'meses_it_vacaciones_prorroga': 18,
}

REFERENCES = {
    'vacaciones_dias_naturales': 'art. 38.1 ET',
    'jornada_semanal_horas_max': 'art. 34.1 ET',
    'jornada_diaria_horas_max': 'art. 34.3 ET',
    'descanso_entre_jornadas_horas': 'art. 34.3 ET',
    'horas_extra_anuales_max': 'art. 35.2 ET',
    'prueba_meses_tecnico_titulado_max': 'art. 14.1 ET',
    'prueba_meses_resto_max': 'art. 14.1 ET',
    'prueba_meses_menos_25_max': 'art. 14.1 ET',
    'preaviso_dias_objetivo': 'art. 53.1.c ET',
    'preaviso_dias_colectivo': 'art. 51.4 ET',
    'nocturnidad_inicio': 'art. 36.1 ET',
    'nocturnidad_fin': 'art. 36.1 ET',
    'semanas_nocturnas_consecutivas_max': 'art. 36.3 ET',
    'meses_it_vacaciones_prorroga': 'art. 38.3 ET',
}

# Dirección de la comparación: True si el valor puede subir sobre el suelo,
# False si solo puede bajar (jornada, horas extra, prueba).
MAYOR_ES_MEJOR = {
    'vacaciones_dias_naturales': True,
    'jornada_semanal_horas_max': False,
    'jornada_diaria_horas_max': False,
    'descanso_entre_jornadas_horas': True,
    'horas_extra_anuales_max': False,
    'prueba_meses_tecnico_titulado_max': False,
    'prueba_meses_resto_max': False,
    'prueba_meses_menos_25_max': False,
    'preaviso_dias_objetivo': True,
    'preaviso_dias_colectivo': True,
    'semanas_nocturnas_consecutivas_max': False,
    'meses_it_vacaciones_prorroga': True,
}


def reference(key):
    return REFERENCES.get(key, 'sin referencia')


def worse_than_floor(key, value):
    """True si `value` deja a la persona peor que el suelo legal."""
    if key not in FLOOR:
        return False
    floor = FLOOR[key]
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return True
    return value < floor if MAYOR_ES_MEJOR[key] else value > floor
