"""Servidor Socket.IO compartido (ASGI).

Vive en ``apps/core`` para que cualquier app pueda reutilizarlo. El servidor
usa ``AsyncRedisManager`` para comunicación cross-process: los workers de
Celery publican eventos vía Redis (ver ``apps.core.realtime.emitter``) y este
proceso ASGI los entrega a las salas ``user_{id}``.
"""

import logging

from django.conf import settings
from asgiref.sync import sync_to_async

import socketio
from socketio import AsyncRedisManager

from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

from apps.iam.models import User

logger = logging.getLogger(__name__)

sio = socketio.AsyncServer(
    async_mode="asgi",
    # Reutiliza los mismos orígenes permitidos que Django (definidos en .env)
    # para que el CORS de Socket.IO no se desincronice del de la API REST.
    cors_allowed_origins=list(settings.CORS_ALLOWED_ORIGINS),
    client_manager=AsyncRedisManager(settings.SOCKETIO_REDIS_URL),
    # Mantiene la conexión WebSocket activa para evitar que daphne
    # cierre el socket por inactividad (timeout ~30s por defecto).
    ping_interval=25,   # El servidor envía un ping cada 25 segundos
    ping_timeout=60,    # El cliente tiene 60 segundos para responder
    logger=True,        # Habilita logs del servidor para depuración
)


@sio.event
async def connect(sid, environ, auth):
    token = auth.get("token") if auth else None
    if not token:
        logger.warning("[SOCKET.IO] Connect rejected (sid=%s): no token", sid)
        return False

    try:
        access_token = AccessToken(token)
        access_token.check_exp()
        user_id = access_token.payload.get("user_id")
    except TokenError as e:
        logger.warning("[SOCKET.IO] Connect rejected (sid=%s): invalid token (%s)", sid, e)
        return False

    try:
        user = await sync_to_async(User.objects.get)(id=user_id)
    except User.DoesNotExist:
        logger.warning("[SOCKET.IO] Connect rejected (sid=%s): user %s not found", sid, user_id)
        return False

    await sio.save_session(sid, {"user_id": user.id})
    await sio.enter_room(sid, f"user_{user.id}")
    logger.info("[SOCKET.IO] Conectado user=%s (sid=%s, room=user_%s)", user.id, sid, user.id)
    return True


@sio.event
async def disconnect(sid):
    try:
        session = await sio.get_session(sid)
        user_id = session.get("user_id")
        if user_id:
            await sio.leave_room(sid, f"user_{user_id}")
            logger.info("[SOCKET.IO] Desconectado user=%s (sid=%s)", user_id, sid)
    except KeyError:
        logger.debug("[SOCKET.IO] Disconnect sin sesion (sid=%s)", sid)
