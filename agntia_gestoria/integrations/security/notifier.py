"""Canal de chat para los avisos de seguridad.

Dos canales mínimos, ambos de salida y sin credenciales en el mensaje:
`MemoryChannel` guarda lo enviado (pruebas y lectura local) y `WebhookChannel`
hace un POST JSON a la URL configurada. Nunca se registra la URL del webhook.
"""
import json
import urllib.error
import urllib.request

MAX_MESSAGE = 3500


class MemoryChannel:
    def __init__(self):
        self.messages = []

    def send(self, text, severity='info'):
        payload = {'text': text[:MAX_MESSAGE], 'severity': severity}
        self.messages.append(payload)
        return payload

    def last(self):
        return self.messages[-1] if self.messages else None


class WebhookChannel:
    def __init__(self, url, timeout=5):
        self._url = url
        self._timeout = timeout

    def send(self, text, severity='info'):
        body = json.dumps({'text': text[:MAX_MESSAGE], 'severity': severity}).encode()
        request = urllib.request.Request(self._url, data=body, method='POST',
                                         headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                return {'delivered': response.status < 300, 'status': response.status}
        except (urllib.error.URLError, OSError, ValueError):
            # Un canal caído no puede tumbar al observador.
            return {'delivered': False, 'status': None}


class Notifier:
    """Envía como mucho un aviso cada `min_seconds` para no inundar el chat."""

    def __init__(self, channel, min_seconds=60, clock=None):
        self._channel = channel
        self._min = min_seconds
        self._clock = clock or (lambda: __import__('time').time())
        self._last = None

    def send(self, text, severity='info'):
        current = self._clock()
        if self._last is not None and current - self._last < self._min:
            return {'delivered': False, 'status': None, 'reason': 'throttled'}
        self._last = current
        result = self._channel.send(text, severity)
        return {**result, 'reason': 'sent'}
