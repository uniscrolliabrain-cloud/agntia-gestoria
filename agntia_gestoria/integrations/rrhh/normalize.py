"""Normalización de tiempos: zona explícita, minutos enteros, sin sorpresas.

Todo intervalo se interpreta en la zona de la empresa y se devuelve en minutos.
Los cambios de horario salen del cálculo absoluto (UTC), no de restar relojes.
"""
from datetime import datetime, time as clock_time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from ..errors import reject


def zone(timezone):
    try:
        return ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, ValueError):
        reject('configuration', 'Zona horaria no válida', 400)


def to_local(value, timezone):
    return datetime.fromisoformat(value).astimezone(zone(timezone))


def minutes_between(start, end):
    """Minutos absolutos entre dos instantes; nunca negativos por construcción."""
    delta = (end - start).total_seconds() / 60
    return int(delta // 1)


def split_by_day(start, end, timezone):
    """Trocea un intervalo que cruza medianoche en tramos ya locales."""
    tz = zone(timezone)
    local_start, local_end = start.astimezone(tz), end.astimezone(tz)
    cursor = local_start
    chunks = []
    while cursor.date() < local_end.date():
        boundary = datetime.combine(cursor.date() + timedelta(days=1),
                                    clock_time.min, tzinfo=tz)
        chunks.append((cursor, boundary))
        cursor = boundary
    chunks.append((cursor, local_end))
    return [(begin, finish) for begin, finish in chunks if finish > begin]


def overlaps(first, second):
    return first[0] < second[1] and second[0] < first[1]
