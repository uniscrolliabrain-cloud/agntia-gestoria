"""Agente de ciberseguridad en modo lectura.

No tiene herramientas de ejecución: solo lee lo observado y lo cuenta en texto
para el chat. Su superficie pública son verbos de lectura (`digest`, `explain`,
`events`, `anomalies`, `chat`); si alguna vez aparece un método que cambie
estado, la prueba de contrato falla a propósito.
"""
from collections import Counter

from .watcher import SEVERITIES

CHAT_PREFIX = 'Seguridad'
AUTH_BURST = 3
SERVER_ERRORS = 2


class SecurityAgent:
    """Resume lo observado sin poder tocar el runtime ni el middleware."""

    name = 'Custodio'
    mode = 'read_only'

    def __init__(self, watcher, notifier=None):
        self._watcher = watcher
        self._notifier = notifier

    def events(self, limit=50):
        return self._watcher.events(limit)

    def explain(self, event):
        return (f"{event['at']} {event['method']} {event['path']} → {event['status']} "
                f"({event['duration_ms']} ms). {event['note']}. "
                f"Actor: {event['actor'] or 'anónimo'}. Gravedad: {event['severity']}.")

    def anomalies(self):
        """Patrones que merecen mirada humana, sin inventar causas."""
        events = self._watcher.events(limit=200)
        found = []
        denied = Counter(event['actor'] for event in events if event['code'] == 'auth_denied')
        for actor, total in sorted(denied.items()):
            if total >= AUTH_BURST:
                found.append({'code': 'auth_burst', 'actor': actor, 'count': total,
                              'detail': f'{total} accesos denegados para el mismo actor'})
        errors = [event for event in events if event['code'] == 'server_error']
        if len(errors) >= SERVER_ERRORS:
            found.append({'code': 'server_errors', 'actor': '', 'count': len(errors),
                          'detail': f'{len(errors)} fallos del servidor en la ventana'})
        for event in events:
            if event['severity'] == 'critical':
                found.append({'code': 'critical_path', 'actor': event['actor'], 'count': 1,
                              'detail': f"Ruta sospechosa: {event['path']}"})
        return found

    def chat(self, limit=20):
        """Historial de lo que el agente ha dicho por el canal configurado."""
        channel = getattr(self._notifier, '_channel', None)
        messages = getattr(channel, 'messages', None)
        if messages is None:
            return {'available': False, 'messages': []}
        return {'available': True, 'messages': messages[-limit:]}

    def digest(self, notify=False):
        counts = self._watcher.counts()
        events = self._watcher.events(limit=200)
        severity = counts['severity']
        alerts = [event for event in events if event['severity'] in ('high', 'critical')]
        anomalies = self.anomalies()
        lines = [
            f"{CHAT_PREFIX} · {counts['total']} peticiones observadas.",
            'Por gravedad: ' + ', '.join(
                f'{name} {severity.get(name, 0)}' for name in SEVERITIES) + '.',
        ]
        if alerts:
            lines.append(f'{len(alerts)} alertas que requieren mirada humana:')
            for event in alerts[:5]:
                lines.append(' · ' + self.explain(event))
        else:
            lines.append('Sin alertas de gravedad alta en la ventana observada.')
        if anomalies:
            lines.append('Patrones:')
            for item in anomalies[:5]:
                lines.append(f" · {item['detail']}.")
        if counts['code']:
            lines.append('Por motivo: ' + ', '.join(
                f'{code} {total}' for code, total in sorted(counts['code'].items())) + '.')
        lines.append('Solo lectura: no he modificado ni bloqueado nada.')
        message = '\n'.join(lines)
        if notify and self._notifier is not None:
            self._notifier.send(message, severity='high' if alerts or anomalies else 'info')
        return {'summary': message, 'counts': counts, 'alerts': alerts,
                'anomalies': anomalies, 'mode': self.mode}

    def watchlist(self):
        """Lo que este agente puede hacer, para que no se le suponga más poder."""
        return {'mode': self.mode,
                'can': ['leer eventos', 'resumir y explicar', 'detectar patrones',
                        'avisar por chat'],
                'cannot': ['bloquear peticiones', 'ejecutar acciones', 'cambiar políticas',
                           'leer credenciales', 'tocar el runtime del agente']}
