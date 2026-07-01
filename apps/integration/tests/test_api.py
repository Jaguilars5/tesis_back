from unittest.mock import patch

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.iam.models import Role
from apps.core.tests.helpers import create_test_user
from ..infrastructure.models import SyncOperationChoices, SyncStatusChoices

User = get_user_model()


class IntegrationAPITest(APITestCase):
    def setUp(self):
        self.role = Role.objects.create(name="Admin")
        self.user = create_test_user(
            email="integration@test.com", dni="7000000001",
            names="Integ", last_names="Test", is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_list_sync_queue(self):
        response = self.client.get("/api/integration/sync-queue/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("apps.integration.tasks.sync_tasks.process_sync_queue_item.delay")
    def test_create_sync_queue(self, mock_delay):
        data = {
            "user": self.user.id,
            "source_table": "student_note",
            "record_uuid": "123e4567-e89b-12d3-a456-426614174000",
            "operation": SyncOperationChoices.CREATE,
            "status": SyncStatusChoices.PENDING,
        }
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post("/api/integration/sync-queue/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_delay.assert_called_once()

    @patch("apps.integration.tasks.sync_tasks.process_sync_queue_item.delay")
    def test_sync_push_queues_operations(self, mock_delay):
        payload = {
            "operations": [
                {
                    "source_table": "student_note",
                    "operation": SyncOperationChoices.CREATE,
                    "record_uuid": "123e4567-e89b-12d3-a456-426614174111",
                    "payload": {"note": "hola"},
                    "client_version": "1.0.0",
                }
            ]
        }
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                "/api/integration/sync/push/", payload, format="json"
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        self.assertTrue(body["ok"])
        self.assertEqual(body["data"]["accepted"], 1)
        self.assertEqual(body["data"]["results"][0]["status"], "QUEUED")
        mock_delay.assert_called_once()

    def test_sync_push_idempotent_operation_is_synced(self):
        from ..infrastructure.repositories import SyncQueueRepository

        operation = {
            "source_table": "student_note",
            "operation": SyncOperationChoices.CREATE,
            "record_uuid": "123e4567-e89b-12d3-a456-426614174222",
        }
        from ..domain.services import SyncQueueService

        idempotency_key = SyncQueueService._build_idempotency_key(
            operation["source_table"],
            operation["record_uuid"],
            operation["operation"],
            operation.get("payload"),
        )
        SyncQueueRepository.create(
            user=self.user,
            source_table=operation["source_table"],
            record_uuid=operation["record_uuid"],
            operation=operation["operation"],
            payload={},
            status=SyncStatusChoices.SYNCED,
            idempotency_key=idempotency_key,
            attempts=0,
        )

        response = self.client.post(
            "/api/integration/sync/push/", {"operations": [operation]}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        self.assertEqual(body["data"]["accepted"], 1)
        self.assertEqual(body["data"]["results"][0]["status"], "DEDUP")

    @patch("apps.integration.tasks.sync_tasks.process_sync_queue_item.delay")
    def test_sync_push_new_sync_version_is_queued(self, mock_delay):
        from ..infrastructure.repositories import SyncQueueRepository
        from ..domain.services import SyncQueueService

        record_uuid = "123e4567-e89b-12d3-a456-426614174555"
        base_op = {
            "source_table": "attendance",
            "operation": SyncOperationChoices.UPDATE,
            "record_uuid": record_uuid,
        }

        key_v2 = SyncQueueService._build_idempotency_key(
            base_op["source_table"],
            base_op["record_uuid"],
            base_op["operation"],
            {"sync_version": 2},
        )
        SyncQueueRepository.create(
            user=self.user,
            source_table=base_op["source_table"],
            record_uuid=record_uuid,
            operation=base_op["operation"],
            payload={"sync_version": 2, "attendance_status_id": 1},
            status=SyncStatusChoices.SYNCED,
            idempotency_key=key_v2,
            attempts=0,
        )

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                "/api/integration/sync/push/",
                {
                    "operations": [
                        {
                            **base_op,
                            "payload": {
                                "sync_version": 3,
                                "attendance_status_id": 2,
                                "class_schedule_id": 10,
                            },
                        }
                    ]
                },
                format="json",
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        self.assertEqual(body["data"]["accepted"], 1)
        self.assertEqual(body["data"]["results"][0]["status"], "QUEUED")
        mock_delay.assert_called_once()

    def test_sync_pull_returns_items(self):
        from ..infrastructure.repositories import SyncQueueRepository

        SyncQueueRepository.create(
            user=self.user,
            source_table="student_note",
            record_uuid="123e4567-e89b-12d3-a456-426614174333",
            operation=SyncOperationChoices.CREATE,
            payload={"a": 1},
            status=SyncStatusChoices.PENDING,
            idempotency_key="pullkey1",
            attempts=0,
        )
        response = self.client.get("/api/integration/sync/pull/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        self.assertTrue(body["ok"])
        self.assertGreaterEqual(body["data"]["count"], 1)

    def test_sync_pull_filters_by_source_table(self):
        from ..infrastructure.repositories import SyncQueueRepository

        SyncQueueRepository.create(
            user=self.user,
            source_table="attendance",
            record_uuid="123e4567-e89b-12d3-a456-426614174444",
            operation=SyncOperationChoices.CREATE,
            payload={},
            status=SyncStatusChoices.PENDING,
            idempotency_key="pullkey2",
            attempts=0,
        )
        response = self.client.get(
            "/api/integration/sync/pull/?source_table=does_not_exist"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["data"]["count"], 0)
