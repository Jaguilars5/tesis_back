from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.academic.academic_period.infrastructure.models import AcademicPeriod
from apps.academic.subject.infrastructure.models import Subject
from apps.academic.subject_academic_config.infrastructure.models import SubjectAcademicConfig
from apps.academic.subject_offering.infrastructure.models import SubjectOffering
from apps.academic.teacher_subject_section.infrastructure.models import TeacherSubjectSection
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.grading.evaluation import BlockComponent, EvaluationBlock, EvaluativeActivity
from apps.grading.qualitative_scale import QualitativeScale
from apps.grading.student_note import StudentNote
from apps.grading.student_note.infrastructure.repositories import EvaluationRepository
from apps.institutions.models import (
    AcademicGrade, AcademicLevel, AcademicSublevel, SchoolYear, Section,
)
from apps.students.models import Enrollment


class WeightedAverageTests(TestCase):
    def setUp(self):
        self.school_year = SchoolYear.objects.create(
            start_date=date(2025, 9, 1), end_date=date(2026, 6, 30),
        )
        self.period = AcademicPeriod.objects.create(
            name="P1", school_year=self.school_year,
            start_date=date(2025, 9, 1), end_date=date(2025, 12, 15),
        )
        self.period2 = AcademicPeriod.objects.create(
            name="P2", school_year=self.school_year,
            start_date=date(2026, 1, 7), end_date=date(2026, 3, 30),
        )
        self.level = AcademicLevel.objects.create(name="EGB")
        self.sublevel = AcademicSublevel.objects.create(
            code="MEDIA", name="Media", academic_level=self.level,
        )
        self.grade = AcademicGrade.objects.create(name="7mo", academic_sublevel=self.sublevel)
        self.section = Section.objects.create(
            code="SEC-A", school_year=self.school_year, parallel="A",
            capacity=30, academic_grade=self.grade,
        )
        self.teacher = create_test_user(email="t@test.com", dni="3000000001")
        self.student = create_test_student(document_number="3000000002")
        self.enrollment = Enrollment.objects.create(
            student=self.student, section=self.section, enrollment_status="ACT",
        )
        self.subject = Subject.objects.create(name="Mate", code="MAT")
        self.config = SubjectAcademicConfig.objects.create(
            subject=self.subject, academic_grade=self.grade, weekly_hours=5,
        )
        self.offering = SubjectOffering.objects.create(
            section=self.section, subject_academic_config=self.config,
        )
        self.tss = TeacherSubjectSection.objects.create(
            user=self.teacher, subject_offering=self.offering,
        )

        # Block A (FORMATIVA, 60%) -> Comp A1 (100%) -> Act1 (50%, /20), Act2 (50%, /10)
        self.block_a = EvaluationBlock.objects.create(
            academic_period=self.period, subject_offering=self.offering,
            name="A", block_type="FORMATIVA", weight_percentage=Decimal("60.00"),
        )
        self.comp_a = BlockComponent.objects.create(
            evaluation_block=self.block_a, name="A1", internal_weight=Decimal("100.00"),
        )
        self.act1 = self._activity(self.comp_a, Decimal("50.00"), Decimal("20.00"))
        self.act2 = self._activity(self.comp_a, Decimal("50.00"), Decimal("10.00"))

        # Block B (SUMATIVA, 40%) -> Comp B1 (100%) -> Act3 (100%, /10)
        self.block_b = EvaluationBlock.objects.create(
            academic_period=self.period, subject_offering=self.offering,
            name="B", block_type="SUMATIVA", weight_percentage=Decimal("40.00"),
        )
        self.comp_b = BlockComponent.objects.create(
            evaluation_block=self.block_b, name="B1", internal_weight=Decimal("100.00"),
        )
        self.act3 = self._activity(self.comp_b, Decimal("100.00"), Decimal("10.00"))

    def _activity(self, component, internal_weight, max_score):
        return EvaluativeActivity.objects.create(
            block_component=component, teacher_subject_section=self.tss,
            title="act", max_score=max_score, internal_weight=internal_weight,
            due_date=date(2025, 10, 15),
        )

    def _note(self, activity, numeric_score=None, qualitative_scale=None,
              manually_overridden=False, grading_mode="NUMERIC"):
        return StudentNote.objects.create(
            enrollment=self.enrollment, evaluative_activity=activity,
            numeric_score=numeric_score, qualitative_scale=qualitative_scale,
            manually_overridden=manually_overridden, grading_mode=grading_mode,
        )

    def _calc(self):
        return EvaluationRepository.calculate_period_average_for_subject(
            self.enrollment.id, self.offering.id, self.period.id,
        )

    def test_full_weighted_hierarchy_with_normalization(self):
        self._note(self.act1, Decimal("20.00"))  # 20/20 -> 10
        self._note(self.act2, Decimal("5.00"))   # 5/10  -> 5  => compA = 7.5, blockA=7.5
        self._note(self.act3, Decimal("8.00"))   # 8/10  -> 8  => blockB = 8

        result = self._calc()
        # final = (60*7.5 + 40*8) / 100 = 7.70
        self.assertEqual(result["final"], Decimal("7.70"))
        self.assertEqual(result["formative"], Decimal("7.50"))
        self.assertEqual(result["summative"], Decimal("8.00"))

    def test_partial_grading_renormalizes(self):
        # Solo se califica Act1 (50% del componente). Debe renormalizar a su peso.
        self._note(self.act1, Decimal("20.00"))  # -> 10

        result = self._calc()
        # compA = (50*10)/50 = 10; blockA = 10; final solo sobre block A presente.
        self.assertEqual(result["final"], Decimal("10.00"))
        self.assertEqual(result["formative"], Decimal("10.00"))
        self.assertEqual(result["summative"], Decimal("0.00"))

    def test_qualitative_uses_numeric_equivalence(self):
        scale = QualitativeScale.objects.create(
            code="DA", description="Domina", numeric_equivalence=Decimal("9.00"),
        )
        self._note(self.act3, qualitative_scale=scale, grading_mode="QUALITATIVE")

        result = self._calc()
        # blockB = 9; final solo block B presente.
        self.assertEqual(result["final"], Decimal("9.00"))
        self.assertEqual(result["summative"], Decimal("9.00"))
        self.assertEqual(result["formative"], Decimal("0.00"))

    def test_period_filter_excludes_other_periods(self):
        self._note(self.act1, Decimal("20.00"))  # 20/20 -> 10
        self._note(self.act2, Decimal("10.00"))  # 10/10 -> 10 => blockA = 10

        # Bloque/actividad en OTRO periodo con nota baja: debe ser ignorado.
        other_block = EvaluationBlock.objects.create(
            academic_period=self.period2, subject_offering=self.offering,
            name="Otro", block_type="FORMATIVA", weight_percentage=Decimal("100.00"),
        )
        other_comp = BlockComponent.objects.create(
            evaluation_block=other_block, name="C", internal_weight=Decimal("100.00"),
        )
        other_act = EvaluativeActivity.objects.create(
            block_component=other_comp, teacher_subject_section=self.tss,
            title="otra", max_score=Decimal("10.00"), internal_weight=Decimal("100.00"),
            due_date=date(2026, 2, 1),
        )
        self._note(other_act, Decimal("1.00"))

        result = self._calc()
        # Solo cuenta el periodo 1 (blockA=10, sin block B). final = 10.00
        self.assertEqual(result["final"], Decimal("10.00"))

    def test_overridden_and_null_notes_skipped(self):
        self._note(self.act1, Decimal("20.00"))                      # cuenta -> 10
        self._note(self.act2, Decimal("2.00"), manually_overridden=True)  # ignorada
        # Act3 sin nota numérica ni cualitativa -> ignorada
        self._note(self.act3, numeric_score=None, grading_mode="QUALITATIVE")

        result = self._calc()
        # compA = (50*10)/50 = 10 (Act2 anulada); block B sin nota válida.
        self.assertEqual(result["final"], Decimal("10.00"))
        self.assertEqual(result["formative"], Decimal("10.00"))
        self.assertEqual(result["summative"], Decimal("0.00"))

    def test_no_notes_returns_none(self):
        self.assertIsNone(self._calc())
