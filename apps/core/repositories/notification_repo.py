"""Repositorio de acceso a datos para notificaciones."""

from django.utils import timezone

from apps.core.models import Notification
from apps.core.repositories.base import BaseRepository


class NotificationRepository(BaseRepository):
    model = Notification

    @classmethod
    def bulk_create_for_users(cls, user_ids, notification_type, title, body="", data=None):
        """Crea una notificación por cada usuario destinatario en un solo round-trip."""
        data = data or {}
        objs = [
            cls.model(
                recipient_id=user_id,
                notification_type=notification_type,
                title=title,
                body=body,
                data=data,
            )
            for user_id in user_ids
        ]
        if not objs:
            return []
        return cls.model.objects.bulk_create(objs)

    @classmethod
    def list_for_user(cls, user):
        return cls.model.objects.filter(recipient=user).order_by("-created_at")

    @classmethod
    def unread_count(cls, user):
        return cls.model.objects.filter(recipient=user, is_read=False).count()

    @classmethod
    def mark_read(cls, notification_id, user):
        notification = cls.model.objects.filter(
            id=notification_id, recipient=user
        ).first()
        if not notification:
            return None
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(update_fields=["is_read", "read_at", "updated_at"])
        return notification

    @classmethod
    def mark_all_read(cls, user):
        return cls.model.objects.filter(recipient=user, is_read=False).update(
            is_read=True, read_at=timezone.now()
        )
