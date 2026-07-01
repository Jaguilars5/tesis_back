from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.core.models import Notification
from apps.core.tests.helpers import create_test_user

BASE = "/api/notifications/notifications/"


class NotificationAPITests(TestCase):
    def setUp(self):
        self.user = create_test_user(email="owner@test.com", dni="900000001")
        self.other = create_test_user(email="other@test.com", dni="900000002")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.n1 = Notification.objects.create(
            recipient=self.user, notification_type="ACTIVITY_CREATED",
            title="A1", body="b1",
        )
        self.n2 = Notification.objects.create(
            recipient=self.user, notification_type="ATTENDANCE_CREATED",
            title="A2", body="b2", is_read=True,
        )
        # Notificación de otro usuario que NUNCA debe aparecer.
        self.foreign = Notification.objects.create(
            recipient=self.other, notification_type="INCIDENT_CREATED",
            title="X", body="x",
        )

    def test_list_returns_only_own_notifications(self):
        resp = self.client.get(BASE)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        results = resp.data["results"]
        ids = {item["id"] for item in results}
        self.assertEqual(ids, {self.n1.id, self.n2.id})

    def test_unread_count(self):
        resp = self.client.get(f"{BASE}unread-count/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["data"]["unread"], 1)

    def test_mark_read(self):
        resp = self.client.post(f"{BASE}{self.n1.id}/mark-read/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.n1.refresh_from_db()
        self.assertTrue(self.n1.is_read)
        self.assertIsNotNone(self.n1.read_at)

    def test_cannot_mark_read_foreign_notification(self):
        resp = self.client.post(f"{BASE}{self.foreign.id}/mark-read/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.foreign.refresh_from_db()
        self.assertFalse(self.foreign.is_read)

    def test_mark_all_read(self):
        resp = self.client.post(f"{BASE}mark-all-read/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(Notification.objects.filter(recipient=self.user, is_read=False).count(), 0)
        # No afecta notificaciones de otros usuarios.
        self.foreign.refresh_from_db()
        self.assertFalse(self.foreign.is_read)

    def test_requires_authentication(self):
        anon = APIClient()
        resp = anon.get(BASE)
        self.assertIn(resp.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
