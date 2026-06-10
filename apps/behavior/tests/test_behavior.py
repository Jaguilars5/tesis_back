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
from apps.grading.models import QualitativeScale
from apps.behavior.models import BehaviorEvaluation, ConductIncident, Severity
from apps.behavior.services.behavior_service import (
    BehaviorEvaluationService,
)
from apps.institutions.models import AcademicGrade, AcademicLevel, AcademicSublevel, SchoolYear, Section
from apps.students.models import Enrollment, EnrollmentStatus


class BehaviorEvaluationModelTest(TestCase):
    """Tests para el modelo BehaviorEvaluation."""

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
        academic_level = AcademicLevel.objects.create(name="Primaria")
        academic_sublevel = AcademicSublevel.objects.create(
            academic_level=academic_level, code="MEDIA", name="Media",
        )
        academic_grade = AcademicGrade.objects.create(
            academic_sublevel=academic_sublevel,
            name="7",
            sequence_order=1,
        )
        section = Section.objects.create(
            school_year=school_year,
            academic_grade=academic_grade,
            parallel="A",
            capacity=30,
        )
        self.student = create_test_student(
            document_number="0912345678",
            names="Juan",
            last_names="Lopez",
            birth_date=date(2010, 1, 1),
        )
        status, _ = EnrollmentStatus.objects.get_or_create(
            code="ACT", defaults={"name": "Activa"}
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            section=section,
            enrollment_status=status,
        )
        self.scale_se, _ = QualitativeScale.objects.get_or_create(
            code="SE",
            defaults={
                "description": "Superior",
                "numeric_equivalence": Decimal("10.00"),
            },
        )
        self.scale_sa, _ = QualitativeScale.objects.get_or_create(
            code="SA",
            defaults={
                "description": "Satisfactorio",
                "numeric_equivalence": Decimal("8.00"),
            },
        )
        self.scale_ac, _ = QualitativeScale.objects.get_or_create(
            code="AC",
            defaults={
                "description": "Aceptable",
                "numeric_equivalence": Decimal("6.00"),
            },
        )
        self.scale_na, _ = QualitativeScale.objects.get_or_create(
            code="NA",
            defaults={
                "description": "No Aceptable",
                "numeric_equivalence": Decimal("4.00"),
            },
        )
        self.severity_leve = Severity.objects.create(
            code="LEVE", name="Falta leve", numeric_level=1,
        )
        self.severity_muy_grave = Severity.objects.create(
            code="MUY_GRAVE", name="Falta muy grave", numeric_level=4,
        )

    def test_create_behavior_evaluation(self):
        evaluation = BehaviorEvaluation.objects.create(
            enrollment=self.enrollment,
            academic_period=self.period,
            calculated_scale=self.scale_se,
        )

        self.assertEqual(evaluation.calculated_scale.code, "SE")
        self.assertIsNone(evaluation.final_scale)
        self.assertIsNone(evaluation.override_reason)

    def test_behavior_evaluation_unique_together(self):
        BehaviorEvaluation.objects.create(
            enrollment=self.enrollment,
            academic_period=self.period,
            calculated_scale=self.scale_se,
        )

        with self.assertRaises(Exception):
            BehaviorEvaluation.objects.create(
                enrollment=self.enrollment,
                academic_period=self.period,
                calculated_scale=self.scale_sa,
            )

    def test_behavior_evaluation_str(self):
        evaluation = BehaviorEvaluation.objects.create(
            enrollment=self.enrollment,
            academic_period=self.period,
            calculated_scale=self.scale_se,
        )

        self.assertIn("Superior", str(evaluation))


class BehaviorEvaluationServiceTest(TestCase):
    """Tests para BehaviorEvaluationService."""

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
            academic_level=academic_level, code="MEDIA", name="Media",
        )
        academic_grade = AcademicGrade.objects.create(
            academic_sublevel=academic_sublevel,
            name="7",
            sequence_order=1,
        )
        section = Section.objects.create(
            school_year=school_year,
            academic_grade=academic_grade,
            parallel="A",
            capacity=30,
        )
        self.subject = Subject.objects.create(name="Matematica", code="MAT-7A")
        subj_config = SubjectAcademicConfig.objects.create(
            subject=self.subject,
            academic_grade=academic_grade,
            weekly_hours=5,
            pedagogical_order=1,
        )
        offering = SubjectOffering.objects.create(
            school_year=school_year,
            section=section,
            subject_academic_config=subj_config,
        )
        self.teacher_subject_section = TeacherSubjectSection.objects.create(
            user=self.user,
            subject_offering=offering,
        )
        self.student = create_test_student(
            document_number="0912345678",
            names="Juan",
            last_names="Lopez",
            birth_date=date(2010, 1, 1),
        )
        status, _ = EnrollmentStatus.objects.get_or_create(
            code="ACT", defaults={"name": "Activa"}
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            section=section,
            enrollment_status=status,
        )
        self.scale_se, _ = QualitativeScale.objects.get_or_create(
            code="SE",
            defaults={
                "description": "Superior",
                "numeric_equivalence": Decimal("10.00"),
            },
        )
        self.scale_sa, _ = QualitativeScale.objects.get_or_create(
            code="SA",
            defaults={
                "description": "Satisfactorio",
                "numeric_equivalence": Decimal("8.00"),
            },
        )
        self.scale_ac, _ = QualitativeScale.objects.get_or_create(
            code="AC",
            defaults={
                "description": "Aceptable",
                "numeric_equivalence": Decimal("6.00"),
            },
        )
        self.scale_na, _ = QualitativeScale.objects.get_or_create(
            code="NA",
            defaults={
                "description": "No Aceptable",
                "numeric_equivalence": Decimal("4.00"),
            },
        )
        self.severity_leve = Severity.objects.create(
            code="LEVE", name="Falta leve", numeric_level=1,
        )
        self.severity_muy_grave = Severity.objects.create(
            code="MUY_GRAVE", name="Falta muy grave", numeric_level=4,
        )

    def test_calculate_no_incidents_returns_se(self):
        evaluation = BehaviorEvaluationService.calculate_behavior_evaluation(
            self.enrollment,
            self.period,
        )

        self.assertEqual(evaluation.calculated_scale.code, "SE")

    def test_calculate_with_minor_incidents_returns_sa(self):
        ConductIncident.objects.create(
            enrollment=self.enrollment,
            reported_by_user=self.user,
            academic_period=self.period,
            incident_date=date(2025, 2, 1),
            category="disciplina",
            severity=self.severity_leve,
        )

        evaluation = BehaviorEvaluationService.calculate_behavior_evaluation(
            self.enrollment,
            self.period,
        )

        self.assertEqual(evaluation.calculated_scale.code, "SA")

    def test_calculate_with_one_serious_incident_returns_ac(self):
        ConductIncident.objects.create(
            enrollment=self.enrollment,
            reported_by_user=self.user,
            academic_period=self.period,
            incident_date=date(2025, 2, 1),
            category="disciplina",
            severity=self.severity_muy_grave,
        )

        evaluation = BehaviorEvaluationService.calculate_behavior_evaluation(
            self.enrollment,
            self.period,
        )

        self.assertEqual(evaluation.calculated_scale.code, "AC")

    def test_calculate_with_multiple_incidents_returns_na(self):
        ConductIncident.objects.create(
            enrollment=self.enrollment,
            reported_by_user=self.user,
            academic_period=self.period,
            incident_date=date(2025, 2, 1),
            category="disciplina",
            severity=self.severity_leve,
        )
        ConductIncident.objects.create(
            enrollment=self.enrollment,
            reported_by_user=self.user,
            academic_period=self.period,
            incident_date=date(2025, 2, 5),
            category="disciplina",
            severity=self.severity_muy_grave,
        )

        evaluation = BehaviorEvaluationService.calculate_behavior_evaluation(
            self.enrollment,
            self.period,
        )

        self.assertEqual(evaluation.calculated_scale.code, "NA")

    def test_override_evaluation(self):
        initial = BehaviorEvaluationService.calculate_behavior_evaluation(
            self.enrollment,
            self.period,
        )
        self.assertEqual(initial.calculated_scale.code, "SE")

        def _test_override(self):
            evaluation = BehaviorEvaluation.objects.get(
                enrollment=self.enrollment,
                academic_period=self.period,
            )
            evaluation.final_scale = self.scale_na
            evaluation.override_reason = "Ajuste manual por comité"
            evaluation.save()

            updated = BehaviorEvaluation.objects.get(
                enrollment=self.enrollment,
                academic_period=self.period,
            )
            self.assertEqual(updated.final_scale.code, "NA")
            self.assertEqual(updated.override_reason, "Ajuste manual por comité")

        _test_override(self)
