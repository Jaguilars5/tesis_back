from django.test import TestCase
from datetime import date
from decimal import Decimal
from apps.institutions.models import AcademicGrade, AcademicLevel, Institution, School_Year
from ..models import Section, Subject, Academic_Activity, Timing_Regime, Config_Academic
from ..services.academic_service import AcademicService


class AcademicServiceTest(TestCase):
    """Tests para AcademicService"""

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
        self.config = Config_Academic.objects.create(
            school_year=self.school_year,
            institution=self.institution,
            academic_period_type="Quimestral",
            number_of_periods=2,
        )
        self.timing_regime = Timing_Regime.objects.create(
            institution=self.institution, name="Matutina"
        )
        self.academic_level = AcademicLevel.objects.create(
            institution=self.institution, name="Primaria"
        )
        self.academic_grade = AcademicGrade.objects.create(
            academic_level=self.academic_level, name="6to", sequence_order=6
        )

    def test_create_section(self):
        """Probar creación de sección"""
        section = AcademicService.create_section(
            school_year_id=self.school_year.id,
            timing_regime_id=self.timing_regime.id,
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
            timing_regime_id=self.timing_regime.id,
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
            timing_regime_id=self.timing_regime.id,
            academic_grade_id=self.academic_grade.id,
            parallel="A",
            capacity=40,
        )
        updated = AcademicService.update_section(section.id, capacity=35)
        self.assertEqual(updated.capacity, 35)

    def test_get_subject(self):
        """Probar obtención de asignatura"""
        subject = AcademicService.create_subject(
            name="Matemática", code="MAT-002"
        )
        retrieved = AcademicService.get_subject(subject.id)
        self.assertEqual(retrieved.id, subject.id)

    def test_update_subject(self):
        """Probar actualización de asignatura"""
        subject = AcademicService.create_subject(
            name="Matemática", code="MAT-003"
        )
        updated = AcademicService.update_subject(subject.id, name="Matemáticas Avanzadas")
        self.assertEqual(updated.name, "Matemáticas Avanzadas")

    def test_timing_regime_operations(self):
        """Probar operaciones de régimen horario"""
        regime = AcademicService.create_timing_regime(
            institution_id=self.institution.id,
            name="Vespertina",
            description="Tarde",
        )
        self.assertIsNotNone(regime.id)

        retrieved = AcademicService.get_timing_regime(regime.id)
        self.assertEqual(retrieved.name, "Vespertina")

        regimes = AcademicService.list_timing_regimes(institution_id=self.institution.id)
        self.assertGreaterEqual(len(regimes), 1)

    def test_create_academic_activity(self):
        """Probar creación de actividad evaluativa"""
        section = AcademicService.create_section(
            school_year_id=self.school_year.id,
            timing_regime_id=self.timing_regime.id,
            academic_grade_id=self.academic_grade.id,
            parallel="A",
            capacity=40,
        )
        subject = AcademicService.create_subject(
            name="Matemática", code="MAT-004"
        )
        activity = AcademicService.create_academic_activity(
            config_academic_id=self.config.id,
            subject_id=subject.id,
            name="Examen Final",
            value_max=20,
            weight=0.5,
            applies_to="all",
        )
        self.assertIsNotNone(activity.id)
        self.assertEqual(activity.name, "Examen Final")

    def test_create_activity_invalid_weight(self):
        """Probar que rechaza peso inválido"""
        subject = AcademicService.create_subject(
            name="Matemática", code="MAT-005"
        )
        with self.assertRaises(ValueError):
            AcademicService.create_academic_activity(
                config_academic_id=self.config.id,
                subject_id=subject.id,
                name="Test",
                value_max=10,
                weight=2.0,
                applies_to="all",
            )
