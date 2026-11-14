"""Lectura acotada del origen.

El middleware no habla ORM libre: pide páginas por tipo y comprueba que todo lo
recibido pertenece a la empresa. Un registro de otra empresa detiene la lectura
antes de normalizar nada. Sin origen configurado, la capacidad no está
disponible en vez de devolver una lista vacía que parezca funcionar.
"""
from dataclasses import dataclass

from ..errors import reject

MAX_PAGES = 200


@dataclass(frozen=True)
class Page:
    records: tuple
    cursor: str | None = None


class Source:
    """Contrato mínimo: tres páginas y un marcador de frescura."""

    name = 'abstract'

    def marker(self, company_id):
        raise NotImplementedError

    def employees(self, company_id, cursor=None):
        raise NotImplementedError

    def punches(self, company_id, period, cursor=None):
        raise NotImplementedError

    def absences(self, company_id, period, cursor=None):
        raise NotImplementedError


class Unavailable(Source):
    name = 'unavailable'

    def _refuse(self, *args, **kwargs):
        reject('capability_unavailable', 'No hay origen de RR. HH. configurado', 503)

    marker = employees = punches = absences = _refuse


class MemorySource(Source):
    """Origen sintético para pruebas y demos; nunca se usa en producción."""

    name = 'memory'

    def __init__(self, *, employees=(), punches=(), absences=(), marker='m1', page_size=2):
        self._employees = tuple(employees)
        self._punches = tuple(punches)
        self._absences = tuple(absences)
        self._marker = marker
        self._size = page_size

    def marker(self, company_id):
        return self._marker

    def _page(self, records, cursor):
        start = int(cursor or 0)
        chunk = records[start:start + self._size]
        following = str(start + self._size) if start + self._size < len(records) else None
        return Page(tuple(chunk), following)

    def employees(self, company_id, cursor=None):
        return self._page(self._employees, cursor)

    def punches(self, company_id, period, cursor=None):
        return self._page(self._punches, cursor)

    def absences(self, company_id, period, cursor=None):
        return self._page(self._absences, cursor)


def read_pages(fetch, *, on_page=None):
    """Pagina hasta el final, rechazando cursores repetidos (bucle del origen)."""
    records, cursor, seen = [], None, set()
    for _ in range(MAX_PAGES):
        page = fetch(cursor)
        if not isinstance(page, Page):
            reject('source_contract', 'El origen no devolvió una página', 502)
        for record in page.records:
            if on_page is not None:
                on_page(record)
            records.append(record)
        if page.cursor is None:
            return records
        if page.cursor in seen:
            reject('source_contract', 'El origen repite el cursor de paginación', 502)
        seen.add(page.cursor)
        cursor = page.cursor
    reject('source_contract', 'El origen no terminó de paginar', 502)


def read_period(source, company_id, period):
    """Lee el periodo completo de una empresa y devuelve datos normalizables."""
    def guard(record):
        owner = record.get('company_id', company_id)
        if owner != company_id:
            reject('outside_scope', 'El origen devolvió un registro de otra empresa', 403)

    marker = source.marker(company_id)
    data = {
        'company_id': company_id,
        'period': period,
        'marker': marker,
        'employees': read_pages(lambda cursor: source.employees(company_id, cursor), on_page=guard),
        'punches': read_pages(lambda cursor: source.punches(company_id, period, cursor), on_page=guard),
        'absences': read_pages(lambda cursor: source.absences(company_id, period, cursor), on_page=guard),
    }
    return data


def reader_for(source, company_id, period):
    """Lector listo para el snapshot: dos lecturas con el mismo marcador."""
    def read():
        return {'marker': source.marker(company_id), 'sources': read_period(source, company_id, period)}
    return read
