"""Superficie del agente de seguridad: solo lectura, solo propietario."""
import os

from fastapi import APIRouter, Depends

from ...auth import Actor, authenticate, require_role
from .agent import SecurityAgent
from .notifier import MemoryChannel, Notifier, WebhookChannel
from .watcher import Watcher


def build_agent(watcher, channel=None):
    if channel is None:
        url = os.getenv('GESTORIA_SECURITY_CHAT_WEBHOOK')
        channel = WebhookChannel(url) if url else MemoryChannel()
    return SecurityAgent(watcher, Notifier(channel))


def register_security_routes(app, watcher, agent=None):
    agent = agent or build_agent(watcher)
    router = APIRouter(prefix='/api/security')

    def owner(actor: Actor = Depends(authenticate)):
        require_role(actor, 'owner')
        return actor

    @router.get('/events')
    def events(limit: int = 50, actor: Actor = Depends(owner)):
        return {'events': agent.events(max(1, min(limit, 200)))}

    @router.get('/digest')
    def digest(actor: Actor = Depends(owner)):
        return agent.digest()

    @router.get('/watchlist')
    def watchlist(actor: Actor = Depends(owner)):
        return agent.watchlist()

    @router.get('/chat')
    def chat(limit: int = 20, actor: Actor = Depends(owner)):
        return agent.chat(max(1, min(limit, 100)))

    @router.post('/report')
    def report(actor: Actor = Depends(owner)):
        return agent.digest(notify=True)

    app.include_router(router)
    return router
