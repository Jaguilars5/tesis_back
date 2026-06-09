from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.iam.models import Role
from apps.core.tests.helpers import create_test_user
from ..models import SyncOperation, SyncStatus

User = get_user_model()


class IntegrationAPITest(APITestCase):
    def setUp(self):
        self.role = Role.objects.create(name="Admin")
        self.user = create_test_user(
            email="integration@test.com", dni="7000000001",
            names="Integ", last_names="Test", is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.op = SyncOperation.objects.create(code="INSERT", name="Insertar")
        self.sync_status = SyncStatus.objects.create(code="PENDIENTE", name="Pendiente")

    def test_list_operations(self):
        response = self.client.get("/api/integration/sync-operations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_operation(self):
        data = {"code": "UPDATE", "name": "Actualizar"}
        response = self.client.post("/api/integration/sync-operations/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_statuses(self):
        response = self.client.get("/api/integration/sync-statuses/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_status(self):
        data = {"code": "PROCESADO", "name": "Procesado"}
        response = self.client.post("/api/integration/sync-statuses/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_sync_queue(self):
        response = self.client.get("/api/integration/sync-queue/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_sync_queue(self):
        data = {
            "user": self.user.id,
            "source_table": "students.Student",
            "record_uuid": "123e4567-e89b-12d3-a456-426614174000",
            "operation": self.op.id,
            "status": self.sync_status.id,
        }
        response = self.client.post("/api/integration/sync-queue/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
