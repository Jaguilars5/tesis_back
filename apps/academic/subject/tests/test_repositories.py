from django.test import TestCase
from ..infrastructure.models import Subject
from ..infrastructure.repositories import SubjectRepository


class SubjectRepositoryTest(TestCase):
    def setUp(self):
        self.subject = Subject.objects.create(name="Matemática", code="MAT-7A")

    def test_create(self):
        obj = SubjectRepository.create(name="Ciencias", code="CIE-7A")
        self.assertEqual(obj.name, "Ciencias")

    def test_get_by_id(self):
        result = SubjectRepository.get_by_id(self.subject.pk)
        self.assertEqual(result.name, "Matemática")

    def test_get_all_ordering(self):
        Subject.objects.create(name="Lengua", code="LEN-7A")
        results = SubjectRepository.get_all(active_only=False)
        self.assertEqual(results.first().name, "Lengua")

    def test_update(self):
        updated = SubjectRepository.update(self.subject.pk, name="Matemáticas")
        self.assertEqual(updated.name, "Matemáticas")
