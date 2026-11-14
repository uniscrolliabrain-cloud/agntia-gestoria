"""Resiliencia del proveedor: disyuntor con sonda y espera indicada.

Si el proveedor falla varias veces seguidas, se deja de llamar y se responde
`provider_unavailable` en vez de acumular timeouts. Pasado el enfriamiento se
permite una sola llamada de sonda: si funciona, se cierra.
"""
import time

from ..errors import IntegrationError


class Breaker:
    def __init__(self, *, threshold=3, cooldown=30, clock=None):
        self._threshold = threshold
        self._cooldown = cooldown
        self._clock = clock or time.monotonic
        self._failures = 0
        self._opened_at = None
        self._probing = False

    @property
    def state(self):
        if self._opened_at is None:
            return 'closed'
        if self._clock() - self._opened_at >= self._cooldown:
            return 'half_open'
        return 'open'

    def call(self, operation):
        if self.state == 'open':
            raise IntegrationError('provider_unavailable',
                                   'El proveedor está temporalmente fuera de servicio',
                                   status=503, retryable=True)
        probing = self.state == 'half_open'
        if probing:
            self._probing = True
        try:
            result = operation()
        except Exception:
            self._failures += 1
            if probing or self._failures >= self._threshold:
                self._opened_at = self._clock()
            raise
        finally:
            self._probing = False
        self._failures = 0
        self._opened_at = None
        return result

    def snapshot(self):
        return {'state': self.state, 'failures': self._failures,
                'threshold': self._threshold, 'cooldown': self._cooldown}


def retry_after_seconds(value, *, default=5, maximum=120):
    """Lee la cabecera del proveedor sin confiar en formatos raros."""
    try:
        seconds = int(str(value).strip())
    except (TypeError, ValueError):
        return default
    return max(0, min(seconds, maximum))
