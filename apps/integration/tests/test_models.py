from django.test import TestCase
from apps.core.tests.helpers import create_test_user
from ..models import SyncQueue
from ..models.syncable_mixin import SyncOperationChoices, SyncStatusChoices


class SyncQueueModelTest(TestCase):
    def test_create_sync_queue(self):
        user = create_test_user(email="test@test.com")
        item = SyncQueue.objects.create(
            user=user,
            source_table="test",
            record_uuid="123",
            operation=SyncOperationChoices.CREATE,
            status=SyncStatusChoices.PENDING,
        )
        self.assertEqual(item.operation, "CREATE")

    def test_unique_idempotency_key(self):
        user = create_test_user(email="test2@test.com")
        SyncQueue.objects.create(
            user=user, source_table="test", record_uuid="456",
            operation=SyncOperationChoices.UPDATE,
        )
        with self.assertRaises(Exception):
            SyncQueue.objects.create(
                user=user, source_table="test", record_uuid="456",
                operation=SyncOperationChoices.UPDATE,
            )
