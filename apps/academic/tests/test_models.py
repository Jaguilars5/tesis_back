from django.test import TestCase
from datetime import date
from apps.institutions.models import AcademicGrade, AcademicLevel, Institution, School_Year
from ..models import Section, Subject, Config_Academic, Academic_Period, Timing_Regime


class SectionModelTest(TestCase):
    """Tests para el modelo Section"""

    def setUp(self):
        """Crear datos de prueba"""
        self.institution = Institution.objects.create(
            name="Colegio Test", code="CT-001", address="Calle Test", city="Quito"
        )
        self.school_year = School_Year.objects.create(
            institution=self.institution,
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )
        self.timing_regime = Timing_Regime.objects.create(
            institution=self.institution, name="Jornada Matutina"
        )
        self.academic_level = AcademicLevel.objects.create(
            institution=self.institution, name="Primaria"
        )
        self.academic_grade = AcademicGrade.objects.create(
            academic_level=self.academic_level, name="6to", sequence_order=6
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            timing_regime=self.timing_regime,
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
        expected = f"{self.institution.name} - 6to A"
        self.assertEqual(str(self.section), expected)

    def test_section_timestamps(self):
        """Probar timestamps"""
        self.assertIsNotNone(self.section.created_at)
        self.assertIsNotNone(self.section.updated_at)


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


class TimingRegimeModelTest(TestCase):
    """Tests para el modelo Timing_Regime"""

    def setUp(self):
        self.institution = Institution.objects.create(
            name="Colegio Test", code="CT-002", address="Calle 2", city="Quito"
        )
        self.regime = Timing_Regime.objects.create(
            institution=self.institution,
            name="Jornada Vespertina",
            description="Tarde: 13:00 - 18:30",
        )

    def test_timing_regime_creation(self):
        """Probar creación de régimen horario"""
        self.assertEqual(self.regime.name, "Jornada Vespertina")
        self.assertEqual(self.regime.description, "Tarde: 13:00 - 18:30")

    def test_multiple_timing_regimes(self):
        """Probar múltiples regímenes en una institución"""
        regimes = [
            Timing_Regime(institution=self.institution, name="Matutina"),
            Timing_Regime(institution=self.institution, name="Nocturna"),
        ]
        Timing_Regime.objects.bulk_create(regimes)
        self.assertEqual(Timing_Regime.objects.count(), 3)
