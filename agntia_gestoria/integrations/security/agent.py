"""Agente de ciberseguridad en modo lectura.

No tiene herramientas de ejecución: solo lee lo observado y lo cuenta en texto
para el chat. Su superficie pública son verbos de lectura (`digest`, `explain`,
`events`); si alguna vez aparece un método que cambie estado, la prueba de
contrato falla a propósito.
"""
from .watcher import SEVERITIES

CHAT_PREFIX = 'Seguridad'


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

    def digest(self, notify=False):
        counts = self._watcher.counts()
        events = self._watcher.events(limit=200)
        severity = counts['severity']
        alerts = [event for event in events if event['severity'] in ('high', 'critical')]
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
        if counts['code']:
            lines.append('Por motivo: ' + ', '.join(
                f'{code} {total}' for code, total in sorted(counts['code'].items())) + '.')
        lines.append('Solo lectura: no he modificado ni bloqueado nada.')
        message = '\n'.join(lines)
        if notify and self._notifier is not None:
            self._notifier.send(message, severity='high' if alerts else 'info')
        return {'summary': message, 'counts': counts, 'alerts': alerts, 'mode': self.mode}

    def watchlist(self):
        """Lo que este agente puede hacer, para que no se le suponga más poder."""
        return {'mode': self.mode,
                'can': ['leer eventos', 'resumir y explicar', 'avisar por chat'],
                'cannot': ['bloquear peticiones', 'ejecutar acciones', 'cambiar políticas',
                           'leer credenciales', 'tocar el runtime del agente']}
