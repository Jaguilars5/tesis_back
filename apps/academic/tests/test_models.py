from django.test import TestCase
from datetime import date, time
from apps.institutions.models import AcademicGrade, AcademicLevel, AcademicSublevel, SchoolYear
from apps.institutions.models import Section
from ..models import Subject, AcademicPeriod, PeriodType, SubjectAcademicConfig, SubjectOffering, TeacherSubjectSection, ClassSchedule, DayOfWeekChoices
from apps.core.tests.helpers import create_test_user


class SectionModelTest(TestCase):
    """Tests para el modelo Section"""

    def setUp(self):
        """Crear datos de prueba"""
        self.school_year = SchoolYear.objects.create(
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )
        self.academic_level = AcademicLevel.objects.create(name="Primaria")
        self.academic_sublevel = AcademicSublevel.objects.create(
            academic_level=self.academic_level, name="Básica"
        )
        self.academic_grade = AcademicGrade.objects.create(
            academic_sublevel=self.academic_sublevel, name="6to"
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
        expected = "6to A"
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


class PeriodTypeModelTest(TestCase):
    """Tests para el modelo PeriodType"""

    def test_period_type_creation(self):
        """Probar creación de tipo de período"""
        period_type = PeriodType.objects.create(
            code="QUIMESTRE",
            name="Quimestre",
            description="Período de evaluación semestral",
            divisions_per_year=2,
        )
        self.assertEqual(period_type.code, "QUIMESTRE")
        self.assertEqual(period_type.name, "Quimestre")
        self.assertEqual(period_type.divisions_per_year, 2)
        self.assertTrue(period_type.is_active)

    def test_period_type_str(self):
        """Probar representación en string"""
        period_type = PeriodType.objects.create(
            code="BIMESTRE",
            name="Bimestre",
            divisions_per_year=4,
        )
        self.assertEqual(str(period_type), "Bimestre")
        self.assertEqual(period_type.divisions_per_year, 4)

    def test_period_type_unique_code(self):
        """Probar restricción de código único"""
        PeriodType.objects.create(code="UNICO", name="Único")
        with self.assertRaises(Exception):
            PeriodType.objects.create(code="UNICO", name="Otro")

    def test_period_type_ordering(self):
        """Probar ordenamiento por nombre"""
        PeriodType.objects.create(code="Z", name="Zorro")
        PeriodType.objects.create(code="A", name="Abeja")
        names = list(PeriodType.objects.values_list("name", flat=True))
        self.assertEqual(names, ["Abeja", "Zorro"])

    def test_period_type_divisions_per_year_default(self):
        """El campo divisions_per_year por defecto es 1"""
        period_type = PeriodType.objects.create(code="ANUAL", name="Anual")
        self.assertEqual(period_type.divisions_per_year, 1)

    def test_period_type_divisions_per_year_positive(self):
        """El campo divisions_per_year no puede ser 0 o negativo"""
        from django.core.exceptions import ValidationError

        period_type = PeriodType(
            code="INVALIDO", name="Inválido", divisions_per_year=0
        )
        with self.assertRaises(ValidationError):
            period_type.full_clean()


class AcademicPeriodModelTest(TestCase):
    """Tests para el modelo AcademicPeriod"""

    def setUp(self):
        self.school_year = SchoolYear.objects.create(
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )
        self.period_type = PeriodType.objects.create(
            code="QUIMESTRE", name="Quimestre", divisions_per_year=2
        )

    def test_academic_period_creation(self):
        """Probar creación de período académico"""
        period = AcademicPeriod.objects.create(
            school_year=self.school_year,
            period_type=self.period_type,
            name="Primer Quimestre",
            start_date=date(2024, 9, 1),
            end_date=date(2024, 12, 15),
        )
        self.assertEqual(period.name, "Primer Quimestre")
        self.assertTrue(period.is_regular_period)
        self.assertTrue(period.is_active)

    def test_academic_period_str(self):
        """Probar representación en string"""
        period = AcademicPeriod.objects.create(
            school_year=self.school_year,
            period_type=self.period_type,
            name="Segundo Quimestre",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 7, 31),
        )
        self.assertEqual(str(period), "Segundo Quimestre")

    def test_academic_period_with_parent(self):
        """Probar período con padre (subperíodo)"""
        parent = AcademicPeriod.objects.create(
            school_year=self.school_year,
            period_type=self.period_type,
            name="Quimestre 1",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 3, 31),
        )
        child = AcademicPeriod.objects.create(
            school_year=self.school_year,
            period_type=self.period_type,
            name="Parcial 1",
            start_date=date(2024, 9, 1),
            end_date=date(2024, 10, 15),
        )
        self.assertIn(child, AcademicPeriod.objects.filter(school_year=self.school_year))


class SubjectAcademicConfigModelTest(TestCase):
    """Tests para el modelo SubjectAcademicConfig"""

    def setUp(self):
        self.subject = Subject.objects.create(name="Matemáticas", code="MAT-001")
        self.level = AcademicLevel.objects.create(name="Secundaria")
        self.sublevel = AcademicSublevel.objects.create(
            academic_level=self.level, name="Básica"
        )
        self.grade = AcademicGrade.objects.create(
            academic_sublevel=self.sublevel, name="1ero"
        )

    def test_config_creation(self):
        """Probar creación de configuración"""
        config = SubjectAcademicConfig.objects.create(
            subject=self.subject,
            academic_grade=self.grade,
            weekly_hours=5        )
        self.assertEqual(config.weekly_hours, 5)
        self.assertTrue(config.is_required)

    def test_config_str(self):
        """Probar representación en string"""
        config = SubjectAcademicConfig.objects.create(
            subject=self.subject,
            academic_grade=self.grade,
            weekly_hours=4        )
        self.assertEqual(str(config), "Matemáticas - 1ero")

    def test_config_unique_subject_grade(self):
        """Probar restricción única subject-grade"""
        SubjectAcademicConfig.objects.create(
            subject=self.subject,
            academic_grade=self.grade,
            weekly_hours=5        )
        with self.assertRaises(Exception):
            SubjectAcademicConfig.objects.create(
                subject=self.subject,
                academic_grade=self.grade,
                weekly_hours=6        )

    def test_config_ordering(self):
        """Probar ordenamiento por orden pedagógico"""
        grade2 = AcademicGrade.objects.create(
            academic_sublevel=self.sublevel, name="2do"
        )
        SubjectAcademicConfig.objects.create(
            subject=self.subject,
            academic_grade=grade2,
            weekly_hours=3        )
        SubjectAcademicConfig.objects.create(
            subject=self.subject,
            academic_grade=self.grade,
            weekly_hours=5        )
        orders = list(
            SubjectAcademicConfig.objects.values_list("subject__name", flat=True)
        )
        self.assertEqual(len(orders), 2)


class SubjectOfferingModelTest(TestCase):
    """Tests para el modelo SubjectOffering"""

    def setUp(self):
        self.school_year = SchoolYear.objects.create(
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )
        self.level = AcademicLevel.objects.create(name="Secundaria")
        self.sublevel = AcademicSublevel.objects.create(
            academic_level=self.level, name="Básica"
        )
        self.grade = AcademicGrade.objects.create(
            academic_sublevel=self.sublevel, name="1ero"
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            academic_grade=self.grade,
            parallel="A",
            capacity=30,
        )
        self.subject = Subject.objects.create(name="Matemáticas", code="MAT-001")
        self.config = SubjectAcademicConfig.objects.create(
            subject=self.subject,
            academic_grade=self.grade,
            weekly_hours=5        )

    def test_offering_creation(self):
        """Probar creación de oferta"""
        offering = SubjectOffering.objects.create(
            section=self.section,
            subject_academic_config=self.config,
        )
        self.assertTrue(offering.is_active)

    def test_offering_str(self):
        """Probar representación en string"""
        offering = SubjectOffering.objects.create(
            section=self.section,
            subject_academic_config=self.config,
        )
        self.assertIn("Matemáticas", str(offering))

    def test_offering_unique_constraint(self):
        """Probar restricción única school_year-section-config"""
        SubjectOffering.objects.create(
            section=self.section,
            subject_academic_config=self.config,
        )
        with self.assertRaises(Exception):
            SubjectOffering.objects.create(
                section=self.section,
                subject_academic_config=self.config,
            )


class TeacherSubjectSectionModelTest(TestCase):
    """Tests para el modelo TeacherSubjectSection"""

    def setUp(self):
        self.school_year = SchoolYear.objects.create(
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )
        self.level = AcademicLevel.objects.create(name="Secundaria")
        self.sublevel = AcademicSublevel.objects.create(
            academic_level=self.level, name="Básica"
        )
        self.grade = AcademicGrade.objects.create(
            academic_sublevel=self.sublevel, name="1ero"
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            academic_grade=self.grade,
            parallel="A",
            capacity=30,
        )
        self.subject = Subject.objects.create(name="Matemáticas", code="MAT-001")
        self.config = SubjectAcademicConfig.objects.create(
            subject=self.subject,
            academic_grade=self.grade,
            weekly_hours=5        )
        self.offering = SubjectOffering.objects.create(
            section=self.section,
            subject_academic_config=self.config,
        )
        self.teacher = create_test_user(
            email="teacher@test.com",
            dni="0102030405",
            names="Juan",
            last_names="Pérez",
        )

    def test_tss_creation(self):
        """Probar creación de asignación docente"""
        tss = TeacherSubjectSection.objects.create(
            user=self.teacher,
            subject_offering=self.offering,
        )
        self.assertTrue(tss.is_active)

    def test_tss_str(self):
        """Probar representación en string"""
        tss = TeacherSubjectSection.objects.create(
            user=self.teacher,
            subject_offering=self.offering,
        )
        self.assertIn("Juan", str(tss))

    def test_tss_unique_user_offering(self):
        """Probar restricción única user-offering"""
        TeacherSubjectSection.objects.create(
            user=self.teacher,
            subject_offering=self.offering,
        )
        with self.assertRaises(Exception):
            TeacherSubjectSection.objects.create(
                user=self.teacher,
                subject_offering=self.offering,
            )


class ClassScheduleModelTest(TestCase):
    """Tests para el modelo ClassSchedule"""

    def setUp(self):
        self.school_year = SchoolYear.objects.create(
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )
        self.level = AcademicLevel.objects.create(name="Secundaria")
        self.sublevel = AcademicSublevel.objects.create(
            academic_level=self.level, name="Básica"
        )
        self.grade = AcademicGrade.objects.create(
            academic_sublevel=self.sublevel, name="1ero"
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            academic_grade=self.grade,
            parallel="A",
            capacity=30,
        )
        self.subject = Subject.objects.create(name="Matemáticas", code="MAT-001")
        self.config = SubjectAcademicConfig.objects.create(
            subject=self.subject,
            academic_grade=self.grade,
            weekly_hours=5        )
        self.offering = SubjectOffering.objects.create(
            section=self.section,
            subject_academic_config=self.config,
        )
        self.teacher = create_test_user(
            email="teacher_sched@test.com",
            dni="0102030406",
            names="María",
            last_names="García",
        )
        self.tss = TeacherSubjectSection.objects.create(
            user=self.teacher,
            subject_offering=self.offering,
        )

    def test_schedule_creation(self):
        """Probar creación de horario"""
        schedule = ClassSchedule.objects.create(
            teacher_subject_section=self.tss,
            day_of_week=DayOfWeekChoices.MONDAY,
            start_time=time(8, 0),
            end_time=time(9, 30),
        )
        self.assertTrue(schedule.is_active)

    def test_schedule_str(self):
        """Probar representación en string"""
        schedule = ClassSchedule.objects.create(
            teacher_subject_section=self.tss,
            day_of_week=DayOfWeekChoices.MONDAY,
            start_time=time(8, 0),
            end_time=time(9, 30),
        )
        self.assertIn("Lunes", str(schedule))

    def test_schedule_ordering(self):
        """Probar ordenamiento por día y hora"""
        ClassSchedule.objects.create(
            teacher_subject_section=self.tss,
            day_of_week=DayOfWeekChoices.WEDNESDAY,
            start_time=time(10, 0),
            end_time=time(11, 30),
        )
        ClassSchedule.objects.create(
            teacher_subject_section=self.tss,
            day_of_week=DayOfWeekChoices.MONDAY,
            start_time=time(8, 0),
            end_time=time(9, 30),
        )
        days = list(
            ClassSchedule.objects.values_list("day_of_week", flat=True)
        )
        self.assertEqual(days, [1, 3])
