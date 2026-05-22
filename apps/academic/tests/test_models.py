from django.test import TestCase
from datetime import date
from apps.institutions.models import AcademicGrade, AcademicLevel, School_Year
from ..models import Section, Subject, Academic_Period


class SectionModelTest(TestCase):
    """Tests para el modelo Section"""

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
        self.section = Section.objects.create(
            school_year=self.school_year,
            academic_grade=self.academic_grade,
            parallel="A",
            capacity=40,
        )

    def test_section_creation(self):
        """Probar creación de sección"""
        self.assertEqual(self.section.parallel, "A")
        self.assertEqual(self.section.capacity, 40)

    def test_section_str(self):
        """Probar representación en string"""
        expected = f"2024-2025 - 6to A"
        self.assertEqual(str(self.section), expected)



class SubjectModelTest(TestCase):
    """Tests para el modelo Subject"""

    def setUp(self):
        """Crear datos de prueba"""
        self.subject = Subject.objects.create(
            name="Matemáticas",
            code="MAT-001",
        )

    def test_subject_creation(self):
        """Probar creación de asignatura"""
        self.assertEqual(self.subject.name, "Matemáticas")
        self.assertEqual(self.subject.code, "MAT-001")

    def test_subject_str(self):
        """Probar representación en string"""
        self.assertEqual(str(self.subject), "Matemáticas")

    def test_multiple_subjects(self):
        """Probar múltiples asignaturas"""
        Subject.objects.create(name="Lengua", code="LEN-001")
        Subject.objects.create(name="Ciencias", code="CIE-001")
        self.assertEqual(Subject.objects.count(), 3)
