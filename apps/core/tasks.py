"""Punto de entrada de tasks de ``apps.core`` para autodiscovery de Celery.

Re-exporta las tasks de notificaciones (que viven en
``apps.core.notifications.tasks``) para que el worker las registre al importar
``apps.core.tasks``.
"""

from apps.core.notifications.tasks import (  # noqa: F401
    notify_activity_created,
    notify_activity_graded,
    notify_attendance_created,
    notify_incident_created,
)

__all__ = [
    "notify_activity_created",
    "notify_activity_graded",
    "notify_attendance_created",
    "notify_incident_created",
]
