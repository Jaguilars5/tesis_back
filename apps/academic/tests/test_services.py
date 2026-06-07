from django.test import TestCase
from datetime import date
from decimal import Decimal
from apps.institutions.models import AcademicGrade, AcademicLevel, School_Year
from apps.institutions.models import Section
from ..models import Subject
from ..services.academic_service import AcademicService


class AcademicServiceTest(TestCase):
    """Tests para AcademicService"""

    def setUp(self):
        """Crear datos de prueba"""
        self.school_year = School_Year.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )
        self.academic_level = AcademicLevel.objects.create(name="Primaria")
        self.academic_grade = AcademicGrade.objects.create(
            academic_level=self.academic_level, name="6to", sequence_order=6
        )

    def test_create_section(self):
        """Probar creación de sección"""
        section = AcademicService.create_section(
            school_year_id=self.school_year.id,
            academic_grade_id=self.academic_grade.id,
            parallel="A",
            capacity=40,
        )
        self.assertIsNotNone(section.id)
        self.assertEqual(section.parallel, "A")

    def test_get_section(self):
        """Probar obtención de sección"""
        section = AcademicService.create_section(
            school_year_id=self.school_year.id,
            academic_grade_id=self.academic_grade.id,
            parallel="B",
            capacity=35,
        )
        retrieved = AcademicService.get_section(section.id)
        self.assertEqual(retrieved.id, section.id)

    def test_create_subject(self):
        """Probar creación de asignatura"""
        subject = AcademicService.create_subject(
            name="Matemática",
            code="MAT-001",
        )
        self.assertIsNotNone(subject.id)
        self.assertEqual(subject.code, "MAT-001")

    def test_update_section(self):
        """Probar actualización de sección"""
        section = AcademicService.create_section(
            school_year_id=self.school_year.id,
            academic_grade_id=self.academic_grade.id,
            parallel="A",
            capacity=40,
        )
        updated = AcademicService.update_section(section.id, capacity=35)
        self.assertEqual(updated.capacity, 35)

    def test_get_subject(self):
        """Probar obtención de asignatura"""
        subject = AcademicService.create_subject(name="Matemática", code="MAT-002")
        retrieved = AcademicService.get_subject(subject.id)
        self.assertEqual(retrieved.id, subject.id)

    def test_update_subject(self):
        """Probar actualización de asignatura"""
        subject = AcademicService.create_subject(name="Matemática", code="MAT-003")
        updated = AcademicService.update_subject(
            subject.id, name="Matemáticas Avanzadas"
        )
        self.assertEqual(updated.name, "Matemáticas Avanzadas")
