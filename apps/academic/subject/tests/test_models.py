from django.test import TestCase
from ..infrastructure.models import Subject


class SubjectModelTest(TestCase):
    def setUp(self):
        self.subject = Subject.objects.create(name="Matemáticas", code="MAT-001")

    def test_subject_creation(self):
        self.assertEqual(self.subject.name, "Matemáticas")
        self.assertEqual(self.subject.code, "MAT-001")
        self.assertTrue(self.subject.is_active)

    def test_subject_str(self):
        self.assertEqual(str(self.subject), "Matemáticas")

    def test_subject_unique_code(self):
        with self.assertRaises(Exception):
            Subject.objects.create(name="Otra", code="MAT-001")
