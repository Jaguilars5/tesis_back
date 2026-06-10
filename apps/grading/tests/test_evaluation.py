from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.academic.models import (PeriodType,
    AcademicPeriod,
    Subject,
    SubjectAcademicConfig,
    SubjectOffering,
    TeacherSubjectSection,
)
from apps.iam.models import Role
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.grading.models import GradeType, EvaluationType, ActivityType
from apps.grading.models import (
    BlockComponent,
    ComponentIndicator,
    EvaluationBlock,
    EvaluativeActivity,
    GradeChangeHistory,
    StudentNote,
)
from apps.grading.services.evaluation_service import EvaluationService
from apps.institutions.models import AcademicGrade, AcademicLevel, AcademicSublevel, SchoolYear, Section
from apps.students.models import Enrollment, EnrollmentStatus


class EvaluationHierarchyTest(TestCase):
    """Tests para la jerarquía EvaluationBlock > BlockComponent > ComponentIndicator > EvaluativeActivity."""

    def setUp(self):
        school_year = SchoolYear.objects.create(
            name="2025",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
        )
        self.period = AcademicPeriod.objects.create(
            school_year=school_year,
            name="P1",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
        )
        self.role = Role.objects.create(name="Docente")
        self.user = create_test_user(
            email="ana@example.com",
            dni="0102030405",
            names="Ana",
            last_names="Perez",
        )
        academic_level = AcademicLevel.objects.create(name="Primaria")
        academic_sublevel = AcademicSublevel.objects.create(
            academic_level=academic_level, code="BASICA", name="Básica"
        )
        academic_grade = AcademicGrade.objects.create(
            academic_sublevel=academic_sublevel, name="7", sequence_order=1,
        )
        self.section = Section.objects.create(
            school_year=school_year,
            academic_grade=academic_grade, parallel="A", capacity=30,
        )
        subject = Subject.objects.create(name="Matematica", code="MAT-7A")
        subj_config = SubjectAcademicConfig.objects.create(
            subject=subject, academic_grade=academic_grade,
            weekly_hours=5, pedagogical_order=1,
        )
        offering = SubjectOffering.objects.create(
            school_year=school_year, section=self.section,
            subject_academic_config=subj_config,
        )
        self.teacher_subject_section = TeacherSubjectSection.objects.create(
            user=self.user, subject_offering=offering,
        )
        self.offering = offering
        self.student = create_test_student(
            document_number="0912345678", names="Juan",
            last_names="Lopez", birth_date=date(2010, 1, 1),
        )

        self.status, _ = EnrollmentStatus.objects.get_or_create(
            code="ACT", defaults={"name": "Activa"}
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student, section=self.section,
            school_year=school_year,
            enrollment_status=self.status,
        )

        self.eval_type_for = EvaluationType.objects.create(
            code="FORMATIVA", name="Formativa"
        )
        self.eval_type_sum = EvaluationType.objects.create(
            code="SUMATIVA", name="Sumativa"
        )
        self.activity_type_examen = ActivityType.objects.create(
            code="EXAMEN", name="Examen"
        )
        self.activity_type_tarea = ActivityType.objects.create(
            code="TAREA", name="Tarea"
        )

    def _create_full_hierarchy(self):
        block = EvaluationBlock.objects.create(
            academic_period=self.period,
            subject_offering=self.offering,
            name="Bloque 1",
            evaluation_type=self.eval_type_for,
            weight_percentage=Decimal("100.00"),
        )
        component = BlockComponent.objects.create(
            evaluation_block=block,
            name="Componente 1",
            internal_weight=Decimal("100.00"),
        )
        indicator = ComponentIndicator.objects.create(
            block_component=component,
            name="Indicador 1",
            internal_weight=Decimal("100.00"),
        )
        activity = EvaluativeActivity.objects.create(
            component_indicator=indicator,
            teacher_subject_section=self.teacher_subject_section,
            title="Examen",
            activity_type=self.activity_type_examen,
            max_score=Decimal("20"),
            due_date=date(2025, 2, 1),
        )
        return block, component, indicator, activity

    def test_create_evaluation_block(self):
        block = EvaluationBlock.objects.create(
            academic_period=self.period,
            subject_offering=self.offering,
            name="Bloque 1",
            evaluation_type=self.eval_type_for,
            weight_percentage=Decimal("50.00"),
        )
        self.assertEqual(block.name, "Bloque 1")
        self.assertEqual(block.weight_percentage, Decimal("50.00"))
        self.assertEqual(block.evaluation_type, self.eval_type_for)

    def test_create_block_component(self):
        block = EvaluationBlock.objects.create(
            academic_period=self.period,
            subject_offering=self.offering,
            name="Bloque 1",
            evaluation_type=self.eval_type_sum,
            weight_percentage=Decimal("100.00"),
        )
        component = BlockComponent.objects.create(
            evaluation_block=block,
            name="Componente 1",
            internal_weight=Decimal("50.00"),
        )
        self.assertEqual(component.name, "Componente 1")
        self.assertEqual(component.internal_weight, Decimal("50.00"))
        self.assertEqual(component.evaluation_block, block)

    def test_create_component_indicator(self):
        block = EvaluationBlock.objects.create(
            academic_period=self.period,
            subject_offering=self.offering,
            name="Bloque 1",
            evaluation_type=self.eval_type_for,
            weight_percentage=Decimal("100.00"),
        )
        component = BlockComponent.objects.create(
            evaluation_block=block, name="Componente 1",
            internal_weight=Decimal("100.00"),
        )
        indicator = ComponentIndicator.objects.create(
            block_component=component, name="Indicador 1",
            internal_weight=Decimal("100.00"),
        )
        self.assertEqual(indicator.name, "Indicador 1")
        self.assertEqual(indicator.block_component, component)

    def test_create_evaluative_activity(self):
        block, component, indicator, activity = self._create_full_hierarchy()

        self.assertEqual(activity.title, "Examen")
        self.assertEqual(activity.max_score, Decimal("20"))
        self.assertEqual(activity.component_indicator, indicator)
        self.assertEqual(activity.activity_type, self.activity_type_examen)

    def test_grade_change_history_creation(self):
        block, component, indicator, activity = self._create_full_hierarchy()
        grade_type = GradeType.objects.create(code="NUM", name="Numerica")

        note = StudentNote.objects.create(
            enrollment=self.enrollment,
            evaluative_activity=activity,
            grade_type=grade_type,
            numeric_score=Decimal("15"),
        )

        history = GradeChangeHistory.objects.create(
            student_note=note,
            modified_by_user=self.user,
            previous_score=Decimal("15"),
            new_score=Decimal("18"),
            reason="Correccion",
        )

        self.assertEqual(history.previous_score, Decimal("15"))
        self.assertEqual(history.new_score, Decimal("18"))
        self.assertEqual(history.reason, "Correccion")


class EvaluationServiceTest(TestCase):
    """Tests para EvaluationService."""

    def setUp(self):
        school_year = SchoolYear.objects.create(
            name="2025",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
        )
        self.period = AcademicPeriod.objects.create(
            school_year=school_year,
            name="P1",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
        )
        self.role = Role.objects.create(name="Docente")
        self.user = create_test_user(
            email="ana@example.com",
            dni="0102030405",
            names="Ana",
            last_names="Perez",
        )
        academic_level = AcademicLevel.objects.create(name="Primaria")
        academic_sublevel = AcademicSublevel.objects.create(
            academic_level=academic_level, code="BASICA", name="Básica"
        )
        academic_grade = AcademicGrade.objects.create(
            academic_sublevel=academic_sublevel, name="7", sequence_order=1,
        )
        self.section = Section.objects.create(
            school_year=school_year,
            academic_grade=academic_grade, parallel="A", capacity=30,
        )
        subject = Subject.objects.create(name="Matematica", code="MAT-7A")
        subj_config = SubjectAcademicConfig.objects.create(
            subject=subject, academic_grade=academic_grade,
            weekly_hours=5, pedagogical_order=1,
        )
        offering = SubjectOffering.objects.create(
            school_year=school_year, section=self.section,
            subject_academic_config=subj_config,
        )
        self.teacher_subject_section = TeacherSubjectSection.objects.create(
            user=self.user, subject_offering=offering,
        )
        self.offering = offering
        self.student = create_test_student(
            document_number="0912345678", names="Juan",
            last_names="Lopez", birth_date=date(2010, 1, 1),
        )

        self.status, _ = EnrollmentStatus.objects.get_or_create(
            code="ACT", defaults={"name": "Activa"}
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student, section=self.section,
            school_year=school_year,
            enrollment_status=self.status,
        )

        self.eval_type_for = EvaluationType.objects.create(
            code="FORMATIVA", name="Formativa"
        )
        self.activity_type_examen = ActivityType.objects.create(
            code="EXAMEN", name="Examen"
        )
        self.activity_type_tarea = ActivityType.objects.create(
            code="TAREA", name="Tarea"
        )

        self.block = EvaluationBlock.objects.create(
            academic_period=self.period,
            subject_offering=self.offering,
            name="Bloque 1",
            evaluation_type=self.eval_type_for,
            weight_percentage=Decimal("100.00"),
        )
        self.component = BlockComponent.objects.create(
            evaluation_block=self.block,
            name="Componente 1",
            internal_weight=Decimal("100.00"),
        )
        self.indicator = ComponentIndicator.objects.create(
            block_component=self.component,
            name="Indicador 1",
            internal_weight=Decimal("100.00"),
        )
        self.activity = EvaluativeActivity.objects.create(
            component_indicator=self.indicator,
            teacher_subject_section=self.teacher_subject_section,
            title="Examen",
            activity_type=self.activity_type_examen,
            max_score=Decimal("10"),
            due_date=date(2025, 2, 1),
        )
        self.grade_type = GradeType.objects.create(code="NUM", name="Numerica")

    def test_calculate_block_grade(self):
        StudentNote.objects.create(
            enrollment=self.enrollment,
            evaluative_activity=self.activity,
            grade_type=self.grade_type,
            numeric_score=Decimal("8"),
        )

        grade = EvaluationService.calculate_block_grade(
            self.enrollment, self.block
        )

        self.assertIsNotNone(grade)
        expected = Decimal("8.00")
        self.assertEqual(grade, expected)

    def test_calculate_block_grade_no_notes(self):
        grade = EvaluationService.calculate_block_grade(
            self.enrollment, self.block
        )

        self.assertIsNone(grade)

    def test_calculate_block_grade_multiple_activities(self):
        indicator2 = ComponentIndicator.objects.create(
            block_component=self.component,
            name="Indicador 2",
            internal_weight=Decimal("100.00"),
        )
        activity2 = EvaluativeActivity.objects.create(
            component_indicator=indicator2,
            teacher_subject_section=self.teacher_subject_section,
            title="Tarea",
            activity_type=self.activity_type_tarea,
            max_score=Decimal("10"),
            due_date=date(2025, 2, 15),
        )
        StudentNote.objects.create(
            enrollment=self.enrollment,
            evaluative_activity=self.activity,
            grade_type=self.grade_type,
            numeric_score=Decimal("8"),
        )
        StudentNote.objects.create(
            enrollment=self.enrollment,
            evaluative_activity=activity2,
            grade_type=self.grade_type,
            numeric_score=Decimal("6"),
        )

        grade = EvaluationService.calculate_block_grade(
            self.enrollment, self.block
        )

        self.assertIsNotNone(grade)

    def test_get_grade_hierarchy(self):
        hierarchy = EvaluationService.get_grade_hierarchy(self.activity)

        self.assertEqual(hierarchy["evaluative_activity"], self.activity)
        self.assertEqual(hierarchy["indicator"], self.indicator)
        self.assertEqual(hierarchy["component"], self.component)
        self.assertEqual(hierarchy["block"], self.block)
        self.assertEqual(hierarchy["academic_period"], self.period)

    def test_create_grade_change_history(self):
        note = StudentNote.objects.create(
            enrollment=self.enrollment,
            evaluative_activity=self.activity,
            grade_type=self.grade_type,
            numeric_score=Decimal("5"),
        )

        history = EvaluationService.create_grade_change_history(
            student_note=note,
            new_score=Decimal("9"),
            user=self.user,
            reason="Error de captura",
        )

        self.assertIsNotNone(history.id)
        self.assertEqual(history.previous_score, Decimal("5"))
        self.assertEqual(history.new_score, Decimal("9"))
        self.assertEqual(history.reason, "Error de captura")
        note.refresh_from_db()
        self.assertEqual(note.numeric_score, Decimal("9"))
        self.assertTrue(note.manually_overridden)
