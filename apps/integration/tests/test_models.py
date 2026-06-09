from django.test import TestCase
from ..models import SyncOperation, SyncStatus


class SyncOperationModelTest(TestCase):
    def setUp(self):
        self.op = SyncOperation.objects.create(code="INSERT", name="Insertar")

    def test_creation(self):
        self.assertEqual(self.op.code, "INSERT")
        self.assertEqual(str(self.op), "Insertar")

    def test_code_unique(self):
        with self.assertRaises(Exception):
            SyncOperation.objects.create(code="INSERT", name="Duplicado")


class SyncStatusModelTest(TestCase):
    def setUp(self):
        self.status = SyncStatus.objects.create(code="PENDIENTE", name="Pendiente")

    def test_creation(self):
        self.assertEqual(self.status.code, "PENDIENTE")
        self.assertEqual(str(self.status), "Pendiente")

    def test_code_unique(self):
        with self.assertRaises(Exception):
            SyncStatus.objects.create(code="PENDIENTE", name="Duplicado")
