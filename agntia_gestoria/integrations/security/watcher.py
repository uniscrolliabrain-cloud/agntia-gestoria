"""Observador de seguridad de solo lectura.

Ve pasar cada petición y la describe, pero no decide, no bloquea y no ejecuta
nada: no tiene acceso al runtime del agente ni puede cambiar su estado. Nunca
guarda cabeceras de credencial ni cuerpos, solo método, ruta, estado, duración y
un actor ya autenticado.
"""
import threading
import time
from collections import Counter, deque
from dataclasses import asdict, dataclass

from ...storage import now, uid

SECRET_HEADERS = ('authorization', 'cookie', 'set-cookie', 'x-api-key',
                  'proxy-authorization', 'x-gestoria-token')

SEVERITIES = ('info', 'warning', 'high', 'critical')


@dataclass(frozen=True)
class Observation:
    event_id: str
    at: str
    method: str
    path: str
    status: int
    duration_ms: int
    actor: str
    company: str
    code: str
    severity: str
    note: str

    def as_dict(self):
        return asdict(self)


def redact(headers):
    """Solo nombres de cabecera no sensibles; jamás valores."""
    result = {}
    for name, value in (headers or {}).items():
        key = name.lower()
        if key in SECRET_HEADERS:
            result[key] = '<redactado>'
            continue
        result[key] = '<oculto>' if key != 'user-agent' else str(value)[:120]
    return result


def classify(method, path, status):
    """Motivo, gravedad y nota de una petición ya terminada."""
    lowered = path.lower()
    if '..' in lowered or '%2e%2e' in lowered or '\x00' in lowered:
        return 'path_traversal', 'critical', 'Ruta con travesía de directorios'
    if status >= 500:
        return 'server_error', 'high', 'El servidor falló al atender la petición'
    if status in (401, 403):
        return 'auth_denied', 'warning', 'Petición sin credencial válida o sin permiso'
    if status == 429:
        return 'rate_limited', 'warning', 'Se alcanzó el límite de peticiones'
    if status >= 400:
        return 'client_error', 'info', 'Petición rechazada por el cliente'
    if method in ('POST', 'PUT', 'PATCH', 'DELETE') and '/rrhh/' in lowered:
        return 'rrhh_write', 'info', 'Operación de cierre o aprobación'
    return 'ok', 'info', 'Petición atendida'


class Watcher:
    """Buffer circular en memoria con contadores por gravedad y por código."""

    def __init__(self, size=500):
        self._events = deque(maxlen=size)
        self._lock = threading.Lock()

    def observe(self, method, path, status, duration_ms, *, actor='anónimo', company=''):
        code, severity, note = classify(method, path, status)
        event = Observation(uid(), now(), method, path[:300], int(status),
                            int(duration_ms), actor, company or '', code, severity, note)
        with self._lock:
            self._events.append(event)
        return event

    def events(self, limit=100):
        with self._lock:
            items = list(self._events)[-limit:]
        return [event.as_dict() for event in reversed(items)]

    def counts(self):
        with self._lock:
            items = list(self._events)
        return {'total': len(items),
                'severity': dict(Counter(event.severity for event in items)),
                'code': dict(Counter(event.code for event in items))}


def timed(watcher, method, path, status, started, *, actor='anónimo', company=''):
    return watcher.observe(method, path, status, (time.perf_counter() - started) * 1000,
                           actor=actor, company=company)
