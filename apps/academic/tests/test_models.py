from django.test import TestCase
from datetime import date
from apps.institutions.models import Institution, School_Year
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
            school_year=self.school_year, name="Jornada Matutina"
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            timing_regime=self.timing_regime,
            level="Primaria",
            grade="6to",
            parallel="A",
            capacity=40,
        )

    def test_section_creation(self):
        """Probar creación de sección"""
        self.assertEqual(self.section.level, "Primaria")
        self.assertEqual(self.section.grade, "6to")
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
        self.institution = Institution.objects.create(
            name="Escuela A", code="EA-001", address="Dir A", city="Quito"
        )
        self.school_year = School_Year.objects.create(
            institution=self.institution,
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )
        self.timing_regime = Timing_Regime.objects.create(
            school_year=self.school_year, name="Matutina"
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            timing_regime=self.timing_regime,
            level="Primaria",
            grade="5to",
            parallel="B",
            capacity=35,
        )
        self.subject = Subject.objects.create(
            school_year=self.school_year,
            section=self.section,
            name="Matemática",
            code="MAT-001",
            weekly_hours=5,
            approve_percentage=70,
        )

    def test_subject_creation(self):
        """Probar creación de asignatura"""
        self.assertEqual(self.subject.name, "Matemática")
        self.assertEqual(self.subject.weekly_hours, 5)

    def test_subject_str(self):
        """Probar representación en string"""
        self.assertIsNotNone(str(self.subject))

    def test_multiple_subjects(self):
        """Probar múltiples asignaturas en una sección"""
        subject_2 = Subject.objects.create(
            school_year=self.school_year,
            section=self.section,
            name="Lenguaje",
            code="LEN-001",
            weekly_hours=3,
            approve_percentage=70,
        )

        subjects = Subject.objects.filter(section=self.section)
        self.assertEqual(subjects.count(), 2)


class ConfigAcademicModelTest(TestCase):
    """Tests para el modelo Config_Academic"""

    def setUp(self):
        """Crear datos de prueba"""
        self.institution = Institution.objects.create(
            name="Instituto B", code="IB-001", address="Dir B", city="Quito"
        )
        self.school_year = School_Year.objects.create(
            institution=self.institution,
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )

    def test_config_creation(self):
        """Probar creación de configuración académica"""
        config = Config_Academic.objects.create(
            school_year=self.school_year,
            institution=self.institution,
            academic_period_type="Quimestral",
            number_of_periods=2,
        )

        self.assertEqual(config.academic_period_type, "Quimestral")
        self.assertEqual(config.number_of_periods, 2)


class TimingRegimeModelTest(TestCase):
    """Tests para el modelo Timing_Regime"""

    def setUp(self):
        """Crear datos de prueba"""
        self.institution = Institution.objects.create(
            name="Colegio C", code="CC-001", address="Dir C", city="Quito"
        )
        self.school_year = School_Year.objects.create(
            institution=self.institution,
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )

    def test_timing_regime_creation(self):
        """Probar creación de régimen horario"""
        regime = Timing_Regime.objects.create(
            school_year=self.school_year,
            name="Jornada Vespertina",
            description="Tarde: 13:00 - 18:30",
        )

        self.assertEqual(regime.name, "Jornada Vespertina")
        self.assertIn("13:00", regime.description)

    def test_multiple_timing_regimes(self):
        """Probar múltiples regímenes en un año"""
        regimes = [
            Timing_Regime(school_year=self.school_year, name="Matutina"),
            Timing_Regime(school_year=self.school_year, name="Vespertina"),
            Timing_Regime(school_year=self.school_year, name="Nocturna"),
        ]
        Timing_Regime.objects.bulk_create(regimes)

        all_regimes = Timing_Regime.objects.filter(school_year=self.school_year)
        self.assertEqual(all_regimes.count(), 3)
