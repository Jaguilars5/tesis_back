from django.test import TestCase
from datetime import date
from ..models import DocumentType, Person


class DocumentTypeModelTest(TestCase):
    def setUp(self):
        self.doc_type = DocumentType.objects.create(code="CC", name="Cédula")

    def test_creation(self):
        self.assertEqual(self.doc_type.code, "CC")
        self.assertEqual(self.doc_type.name, "Cédula")
        self.assertTrue(self.doc_type.is_active)

    def test_code_unique(self):
        with self.assertRaises(Exception):
            DocumentType.objects.create(code="CC", name="Duplicado")

    def test_str(self):
        self.assertEqual(str(self.doc_type), "Cédula")


class PersonModelTest(TestCase):
    def setUp(self):
        self.doc_type = DocumentType.objects.create(code="CC", name="Cédula")
        self.person = Person.objects.create(
            document_type=self.doc_type,
            document_number="1234567890",
            names="Juan",
            last_names="Pérez",
            birth_date=date(2000, 1, 15),
            email="juan@example.com",
        )

    def test_creation(self):
        self.assertEqual(self.person.names, "Juan")
        self.assertEqual(self.person.document_number, "1234567890")
        self.assertTrue(self.person.is_active)

    def test_full_name(self):
        self.assertEqual(self.person.get_full_name(), "Juan Pérez")

    def test_str(self):
        self.assertEqual(str(self.person), "Juan Pérez")

    def test_get_age(self):
        self.assertIsNotNone(self.person.get_age())

    def test_get_age_no_birth_date(self):
        person = Person.objects.create(
            document_type=self.doc_type,
            document_number="0987654321",
            names="Ana",
            last_names="López",
        )
        self.assertIsNone(person.get_age())
