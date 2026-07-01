from unittest import mock

from django.core import mail
from django.test import TestCase

from apps.core.models import Notification
from apps.core.notifications.service import NotificationService
from apps.core.tests.helpers import create_test_user


class NotificationServiceTests(TestCase):
    def setUp(self):
        self.u1 = create_test_user(email="u1@test.com", dni="910000001")
        self.u2 = create_test_user(email="u2@test.com", dni="910000002")
        # Usuario sin email -> no debe recibir correo, pero sí notificación.
        self.u3 = create_test_user(email="", dni="910000003")

    @mock.patch("apps.core.notifications.service.emit_to_user")
    def test_notify_persists_emits_and_emails(self, mock_emit):
        result = NotificationService.notify(
            user_ids=[self.u1.id, self.u2.id, self.u3.id],
            notification_type="ACTIVITY_CREATED",
            title="Nueva actividad",
            body="Cuerpo",
            data={"activity_id": 5},
        )

        self.assertEqual(result["persisted"], 3)
        self.assertEqual(result["emitted"], 3)
        self.assertEqual(result["emails"], 2)  # u3 sin email

        self.assertEqual(Notification.objects.count(), 3)
        n = Notification.objects.filter(recipient=self.u1).first()
        self.assertEqual(n.notification_type, "ACTIVITY_CREATED")
        self.assertEqual(n.data, {"activity_id": 5})

        self.assertEqual(mock_emit.call_count, 3)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, "Nueva actividad")

    @mock.patch("apps.core.notifications.service.emit_to_user")
    def test_notify_deduplicates_recipients(self, mock_emit):
        result = NotificationService.notify(
            user_ids=[self.u1.id, self.u1.id, None],
            notification_type="ACTIVITY_GRADED",
            title="T",
        )
        self.assertEqual(result["persisted"], 1)
        self.assertEqual(Notification.objects.filter(recipient=self.u1).count(), 1)
        self.assertEqual(mock_emit.call_count, 1)

    @mock.patch("apps.core.notifications.service.emit_to_user")
    def test_notify_send_email_false(self, mock_emit):
        NotificationService.notify(
            user_ids=[self.u1.id],
            notification_type="ACTIVITY_GRADED",
            title="T",
            send_email=False,
        )
        self.assertEqual(len(mail.outbox), 0)
        mock_emit.assert_called_once()

    @mock.patch("apps.core.notifications.service.emit_to_user")
    def test_notify_empty_recipients_noop(self, mock_emit):
        result = NotificationService.notify(
            user_ids=[],
            notification_type="ACTIVITY_GRADED",
            title="T",
        )
        self.assertEqual(result, {"persisted": 0, "emitted": 0, "emails": 0})
        mock_emit.assert_not_called()
        self.assertEqual(Notification.objects.count(), 0)
