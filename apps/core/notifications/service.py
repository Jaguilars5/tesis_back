"""Servicio de despacho de notificaciones (multi-canal).

Persiste las notificaciones, las emite en tiempo real (Socket.IO) y, si
procede, envía correo electrónico al ``person.email`` del destinatario.
Reutiliza el patrón del aviso de inasistencia.
"""

import logging

from apps.core.realtime.emitter import emit_to_user
from apps.core.repositories.notification_repo import NotificationRepository

logger = logging.getLogger(__name__)


class NotificationService:
    @staticmethod
    def notify(user_ids, notification_type, title, body="", data=None, send_email=True):
        """Despacha una notificación a varios usuarios por los tres canales.

        - Persiste una fila ``Notification`` por destinatario (bulk).
        - Emite el evento ``notification`` a cada sala ``user_{id}`` vía Redis.
        - Envía correo a ``user.person.email`` cuando existe y ``send_email``.

        Args:
            user_ids: iterable de IDs de usuario destinatarios (se deduplica).
            notification_type: valor de ``NotificationType``.
            title: título de la notificación.
            body: cuerpo/descripción.
            data: payload JSON adicional (default ``{}``).
            send_email: si ``True``, envía correo a los que tengan email.

        Returns:
            dict con conteos de persistidas/emitidas/correos enviados.
        """
        data = data or {}
        unique_ids = list(dict.fromkeys(uid for uid in user_ids if uid))
        if not unique_ids:
            return {"persisted": 0, "emitted": 0, "emails": 0}

        NotificationRepository.bulk_create_for_users(
            user_ids=unique_ids,
            notification_type=notification_type,
            title=title,
            body=body,
            data=data,
        )

        payload = {
            "type": notification_type,
            "title": title,
            "body": body,
            "data": data,
        }

        emitted = 0
        for uid in unique_ids:
            emit_to_user(uid, "notification", payload)
            emitted += 1

        emails_sent = 0
        if send_email:
            emails_sent = NotificationService._send_emails(unique_ids, title, body)

        logger.info(
            "Notificación %s despachada: persisted=%s emitted=%s emails=%s",
            notification_type, len(unique_ids), emitted, emails_sent,
        )
        return {"persisted": len(unique_ids), "emitted": emitted, "emails": emails_sent}

    @staticmethod
    def _send_emails(user_ids, title, body):
        from django.conf import settings
        from django.core.mail import send_mail

        from apps.iam.models import User

        users = User.objects.filter(id__in=user_ids).select_related("person")
        sent = 0
        for user in users:
            person = getattr(user, "person", None)
            email = getattr(person, "email", "") if person else ""
            if not email:
                continue
            send_mail(
                subject=title,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
            sent += 1
        return sent
