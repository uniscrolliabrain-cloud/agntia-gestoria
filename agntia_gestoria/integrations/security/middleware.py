"""Middleware de observación.

Registra cada petición terminada, incluidas las que fallan con excepción. No
lee cuerpos ni cabeceras de credencial y no altera la respuesta.
"""
import time

from starlette.middleware.base import BaseHTTPMiddleware

from .watcher import timed


class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, watcher):
        super().__init__(app)
        self.watcher = watcher

    async def dispatch(self, request, call_next):
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            timed(self.watcher, request.method, request.url.path, 500, started)
            raise
        timed(self.watcher, request.method, request.url.path, response.status_code, started)
        return response
