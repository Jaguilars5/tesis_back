"""Emisor de eventos Socket.IO para workers (Celery).

Función única y reutilizable que publica un evento a la sala ``user_{id}`` vía
Redis usando el protocolo nativo de python-socketio, de modo que el servidor
ASGI (``apps.core.realtime.server``) lo entregue al cliente conectado.

Deduplica las dos copias previas que vivían en ``apps.analytics.tasks`` y
``apps.attendance.attendance_core.tasks``.
"""

import json
import logging
import uuid

logger = logging.getLogger(__name__)


def emit_to_user(user_id, event, data):
    """Publica ``event`` con ``data`` a la sala ``user_{user_id}`` vía Redis.

    Falla en silencio (solo log) para que un problema de mensajería en tiempo
    real nunca rompa la transacción de negocio que la disparó.
    """
    _publish(event, data, room=f"user_{user_id}")
    logger.info("[SOCKET.IO] Evento %s publicado a Redis para user_%s", event, user_id)


def emit_to_all(event, data):
    """Publica ``event`` con ``data`` a todos los clientes conectados vía Redis.

    Similar a emit_to_user pero sin filtrar por sala (broadcast global).
    """
    _publish(event, data)
    logger.info("[SOCKET.IO] Evento %s emitido globalmente", event)


def _publish(event, data, room=None):
    """Internal helper: publica un mensaje Socket.IO en Redis."""
    try:
        import redis as redis_lib
        from django.conf import settings

        message = {"method": "emit", "event": event, "data": [data], "binary": False, "namespace": "/", "skip_sid": None, "callback": None, "host_id": str(uuid.uuid4())}
        if room:
            message["room"] = room

        r = redis_lib.Redis.from_url(settings.SOCKETIO_REDIS_URL)
        r.publish("socketio", json.dumps(message))
        r.close()
    except Exception:
        logger.warning("[SOCKET.IO] No se pudo publicar evento a Redis", exc_info=True)
