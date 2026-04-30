from django.test import TestCase
from datetime import date
from decimal import Decimal
from apps.institutions.models import Institution, School_Year
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
            school_year=self.school_year, name="Matutina"
        )

    def test_create_section(self):
        """Probar creación de sección"""
        section = AcademicService.create_section(
            school_year_id=self.school_year.id,
            timing_regime_id=self.timing_regime.id,
            level="Primaria",
            grade="6to",
            parallel="A",
            capacity=40,
        )

        self.assertIsNotNone(section.id)
        self.assertEqual(section.grade, "6to")
        self.assertEqual(section.parallel, "A")

    def test_create_section_duplicate(self):
        """Probar que no permite secciones duplicadas"""
        AcademicService.create_section(
            school_year_id=self.school_year.id,
            timing_regime_id=self.timing_regime.id,
            level="Primaria",
            grade="6to",
            parallel="A",
            capacity=40,
        )

        with self.assertRaises(ValueError):
            AcademicService.create_section(
                school_year_id=self.school_year.id,
                timing_regime_id=self.timing_regime.id,
                level="Primaria",
                grade="6to",
                parallel="A",
                capacity=35,
            )

    def test_get_section(self):
        """Probar obtención de sección"""
        section = AcademicService.create_section(
            school_year_id=self.school_year.id,
            timing_regime_id=self.timing_regime.id,
            level="Primaria",
            grade="5to",
            parallel="B",
            capacity=35,
        )

        retrieved = AcademicService.get_section(section.id)
        self.assertEqual(retrieved.id, section.id)

    def test_create_subject(self):
        """Probar creación de asignatura"""
        section = AcademicService.create_section(
            school_year_id=self.school_year.id,
            timing_regime_id=self.timing_regime.id,
            level="Primaria",
            grade="6to",
            parallel="A",
            capacity=40,
        )

        subject = AcademicService.create_subject(
            school_year_id=self.school_year.id,
            section_id=section.id,
            name="Matemática",
            code="MAT-001",
            weekly_hours=3,
        )

        self.assertIsNotNone(subject.id)
        self.assertEqual(subject.name, "Matemática")

    def test_create_subject_invalid_section(self):
        """Probar que rechaza sección inválida"""
        with self.assertRaises(ValueError):
            AcademicService.create_subject(
                school_year_id=self.school_year.id,
                section_id=9999,  # No existe
                name="Matemática",
                code="MAT-001",
                weekly_hours=5,
            )

    def test_list_subjects_by_section(self):
        """Probar listado de asignaturas por sección"""
        section = AcademicService.create_section(
            school_year_id=self.school_year.id,
            timing_regime_id=self.timing_regime.id,
            level="Primaria",
            grade="6to",
            parallel="A",
            capacity=40,
        )

        AcademicService.create_subject(
            school_year_id=self.school_year.id,
            section_id=section.id,
            name="Matemática",
            code="MAT-001",
            weekly_hours=5,
        )
        AcademicService.create_subject(
            school_year_id=self.school_year.id,
            section_id=section.id,
            name="Lenguaje",
            code="LEN-001",
            weekly_hours=4,
        )

        subjects = AcademicService.list_subjects_by_section(section.id)
        self.assertEqual(subjects.count(), 2)

    def test_create_academic_activity(self):
        """Probar creación de actividad evaluativa"""
        section = AcademicService.create_section(
            school_year_id=self.school_year.id,
            timing_regime_id=self.timing_regime.id,
            level="Primaria",
            grade="6to",
            parallel="A",
            capacity=40,
        )

        subject = AcademicService.create_subject(
            school_year_id=self.school_year.id,
            section_id=section.id,
            name="Matemática",
            code="MAT-001",
            weekly_hours=5,
        )

        activity = AcademicService.create_academic_activity(
            config_academic_id=self.config.id,
            subject_id=subject.id,
            name="Examen Quimestral",
            value_max=20,
            weight=0.5,
            applies_to="all",
            order=1,
        )

        self.assertIsNotNone(activity.id)
        self.assertEqual(activity.value_max, 20)
        self.assertEqual(activity.weight, 0.5)

    def test_create_activity_invalid_weight(self):
        """Probar que rechaza peso inválido"""
        section = AcademicService.create_section(
            school_year_id=self.school_year.id,
            timing_regime_id=self.timing_regime.id,
            level="Primaria",
            grade="6to",
            parallel="A",
            capacity=40,
        )

        subject = AcademicService.create_subject(
            school_year_id=self.school_year.id,
            section_id=section.id,
            name="Matemática",
            code="MAT-001",
            weekly_hours=5,
        )

        with self.assertRaises(ValueError):
            AcademicService.create_academic_activity(
                config_academic_id=self.config.id,
                subject_id=subject.id,
                name="Examen",
                value_max=20,
                weight=1.5,  # Inválido
                applies_to="all",
            )

    def test_update_section(self):
        """Probar actualización de sección"""
        section = AcademicService.create_section(
            school_year_id=self.school_year.id,
            timing_regime_id=self.timing_regime.id,
            level="Primaria",
            grade="6to",
            parallel="A",
            capacity=40,
        )

        updated = AcademicService.update_section(section.id, capacity=45)

        self.assertEqual(updated.capacity, 45)

    def test_timing_regime_operations(self):
        """Probar operaciones de régimen horario"""
        regime = AcademicService.create_timing_regime(
            school_year_id=self.school_year.id, name="Vespertina"
        )

        self.assertIsNotNone(regime.id)

        retrieved = AcademicService.get_timing_regime(regime.id)
        self.assertEqual(retrieved.id, regime.id)
