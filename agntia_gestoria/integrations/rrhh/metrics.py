"""Métricas por capacidad: cuántas, cuánto tardan y cuántas fallan.

Etiquetas cerradas (capacidad y resultado), nunca datos de empresa ni de
persona. Percentiles calculados sobre la muestra real de la ventana.
"""
import threading
from collections import defaultdict

OUTCOMES = ('ok', 'error', 'blocked')


class Metrics:
    def __init__(self, window=500):
        self._window = window
        self._lock = threading.Lock()
        self._samples = defaultdict(list)
        self._counts = defaultdict(lambda: defaultdict(int))

    def observe(self, capability, outcome, duration_ms=0):
        if outcome not in OUTCOMES:
            raise ValueError('Resultado no admitido')
        with self._lock:
            self._counts[capability][outcome] += 1
            samples = self._samples[capability]
            samples.append(max(0, int(duration_ms)))
            if len(samples) > self._window:
                samples.pop(0)

    @staticmethod
    def _percentile(values, fraction):
        if not values:
            return None
        ordered = sorted(values)
        index = min(len(ordered) - 1, max(0, int(round(fraction * (len(ordered) - 1)))))
        return ordered[index]

    def snapshot(self):
        with self._lock:
            data = {capability: {'counts': dict(counts),
                                 'p50_ms': self._percentile(self._samples[capability], 0.50),
                                 'p95_ms': self._percentile(self._samples[capability], 0.95),
                                 'sample': len(self._samples[capability])}
                    for capability, counts in self._counts.items()}
        return {'capabilities': data,
                'total': sum(sum(item['counts'].values()) for item in data.values())}


GLOBAL = Metrics()
