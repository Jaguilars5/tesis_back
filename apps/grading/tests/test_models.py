from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.academic.models import (PeriodType,
    AcademicPeriod,
    Subject,
    SubjectAcademicConfig,
    SubjectOffering,
    TeacherSubjectSection,
)
from apps.iam.models import Role, User
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.grading.models import ActivityType, EvaluationType, GradeType, QualitativeScale
from apps.grading.models import (
    EvaluativeActivity,
    BlockComponent,
    EvaluationBlock,
    ComponentIndicator,
    StudentNote,
)
from apps.institutions.models import AcademicGrade, AcademicLevel, AcademicSublevel, SchoolYear, Section
from apps.students.models import Enrollment, EnrollmentStatus, Student


class GradingModelTest(TestCase):
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
        self.academic_level = AcademicLevel.objects.create(name="Primaria")
        self.academic_sublevel = AcademicSublevel.objects.create(
            academic_level=self.academic_level, code="MEDIA", name="Media"
        )
        self.academic_grade = AcademicGrade.objects.create(
            academic_sublevel=self.academic_sublevel,
            name="7",
            sequence_order=1,
        )
        self.section = Section.objects.create(
            school_year=school_year,
            academic_grade=self.academic_grade,
            parallel="A",
            capacity=30,
        )
        self.subject = Subject.objects.create(
            name="Matemática",
            code="MAT-7A",
        )
        subj_config = SubjectAcademicConfig.objects.create(
            subject=self.subject,
            academic_grade=self.academic_grade,
            weekly_hours=5,
            pedagogical_order=1,
        )
        offering = SubjectOffering.objects.create(
            school_year=school_year,
            section=self.section,
            subject_academic_config=subj_config,
        )
        self.teacher_subject_section = TeacherSubjectSection.objects.create(
            user=self.user,
            subject_offering=offering,
        )
        self.offering = offering
        self.student = create_test_student(
            document_number="0912345678",
            names="Juan",
            last_names="Lopez",
            birth_date=date(2010, 1, 1),
        )

    def _create_enrollment(self):
        status, _ = EnrollmentStatus.objects.get_or_create(
            code="ACT", defaults={"name": "Activa"}
        )
        return Enrollment.objects.create(
            student=self.student,
            section=self.section,
            enrollment_status=status,
        )

    def _create_class_assignment(self, max_score=20):
        eval_type, _ = EvaluationType.objects.get_or_create(
            code="FORMATIVA", defaults={"name": "Formativa"}
        )
        macro = EvaluationBlock.objects.create(
            academic_period=self.period,
            subject_offering=self.offering,
            name="Macro 1",
            evaluation_type=eval_type,
            weight_percentage=Decimal("100.00"),
        )
        criteria = BlockComponent.objects.create(
            evaluation_block=macro,
            name="Criterio 1",
            internal_weight=Decimal("100.00"),
        )
        subcriteria = ComponentIndicator.objects.create(
            block_component=criteria,
            name="Subcriterio 1",
            internal_weight=Decimal("100.00"),
        )
        act_type, _ = ActivityType.objects.get_or_create(
            code="EXAMEN", defaults={"name": "Examen"}
        )
        return EvaluativeActivity.objects.create(
            component_indicator=subcriteria,
            teacher_subject_section=self.teacher_subject_section,
            title="Examen",
            activity_type=act_type,
            max_score=Decimal(str(max_score)),
            due_date=date(2025, 2, 1),
        )

    def test_student_note_validation(self):
        enrollment = self._create_enrollment()
        evaluative_activity = self._create_class_assignment(max_score=20)
        note = StudentNote(
            enrollment=enrollment,
            evaluative_activity=evaluative_activity,
            numeric_score=Decimal("25"),
        )
        with self.assertRaises(ValidationError):
            note.full_clean()


class GradeTypeModelTest(TestCase):
    def setUp(self):
        self.grade_type = GradeType.objects.create(code="NUM", name="Numérica")

    def test_creation(self):
        self.assertEqual(self.grade_type.code, "NUM")
        self.assertEqual(self.grade_type.name, "Numérica")

    def test_code_unique(self):
        with self.assertRaises(Exception):
            GradeType.objects.create(code="NUM", name="Duplicado")

    def test_str(self):
        self.assertEqual(str(self.grade_type), "Numérica")


class QualitativeScaleModelTest(TestCase):
    def setUp(self):
        self.scale = QualitativeScale.objects.create(
            code="SE", description="Superior", numeric_equivalence=9.0
        )

    def test_creation(self):
        self.assertEqual(self.scale.code, "SE")
        self.assertEqual(self.scale.description, "Superior")
        self.assertEqual(self.scale.numeric_equivalence, 9.0)

    def test_code_unique(self):
        with self.assertRaises(Exception):
            QualitativeScale.objects.create(
                code="SE", description="Duplicado", numeric_equivalence=8.0
            )

    def test_str(self):
        self.assertEqual(str(self.scale), "SE — Superior")
