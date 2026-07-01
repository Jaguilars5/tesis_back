"""
ASGI config for academic_system project.

Monta Socket.IO (python-socketio) junto con la aplicación ASGI de Django.
Socket.IO usa AsyncRedisManager para comunicación cross-process (Celery).
"""

import os

from django.core.asgi import get_asgi_application

from socketio import ASGIApp

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

django_asgi = get_asgi_application()

from apps.core.realtime.server import sio

application = ASGIApp(sio, other_asgi_app=django_asgi)
