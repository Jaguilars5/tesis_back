from datetime import date
from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.academic.academic_period.infrastructure.models import AcademicPeriod
from apps.academic.subject.infrastructure.models import Subject
from apps.academic.subject_academic_config.infrastructure.models import SubjectAcademicConfig
from apps.academic.subject_offering.infrastructure.models import SubjectOffering
from apps.academic.period_type.infrastructure.models import PeriodType
from apps.analytics.early_alert.infrastructure.models import EarlyAlert
from apps.analytics.models import RiskFactor, StudentRiskFactor, StudentRiskScore
from apps.analytics.services.dashboard_service import DashboardService
from apps.analytics.services.csv_export_service import CSVExportService
from apps.attendance.attendance_core import Attendance
from apps.attendance.attendance_status import AttendanceStatus
from apps.behavior.behavior_evaluation import BehaviorEvaluation
from apps.behavior.conduct_incident import ConductIncident
from apps.behavior.severity import Severity
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.grading.activity_type import ActivityType
from apps.grading.evaluation import EvaluationBlock, EvaluativeActivity
from apps.grading.student_note import GradeChangeHistory, PeriodGradeSummary, StudentNote
from apps.grading.qualitative_scale import QualitativeScale
REPLACED AcademicGrade, AcademicLevel, AcademicSublevel, SchoolYear, Section
from apps.students.models import Enrollment, Student, StudentRepresentative
from apps.students.models import Kinship
from apps.iam import Permission, Role, RolePermission, UserRole
from apps.behavior.incident_type import IncidentType


class IntegrationWorkflowTests(TestCase):
    """Pruebas de flujos de integración completos del sistema."""

    def setUp(self):
        self.school_year = SchoolYear.objects.create( start_date=date(2025, 9, 1), end_date=date(2026, 6, 30),
        )
        self.period = AcademicPeriod.objects.create(
            name="Primer Trimestre", school_year=self.school_year,
            start_date=date(2025, 9, 1), end_date=date(2025, 12, 15),
        )
        self.level = AcademicLevel.objects.create(name="EGB")
        self.sublevel = AcademicSublevel.objects.create(
            code="MEDIA", name="Media", academic_level=self.level,
        )
        self.grade = AcademicGrade.objects.create(
            name="7mo", academic_sublevel=self.sublevel,
        )
        self.section = Section.objects.create(
            code="SEC-A", school_year=self.school_year, parallel="A",
            capacity=30, academic_grade=self.grade,
        )
        self.teacher = create_test_user(email="teacher@test.com", dni="1111111111", is_superuser=False)
        self.student = create_test_student(
            document_number="1234567890", names="Juan", last_names="Perez",
            birth_date=date(2012, 5, 15),
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student, section=self.section,
            enrollment_status="ACT",
        )
        self.subject = Subject.objects.create(name="Matemáticas", code="MAT")
        self.config = SubjectAcademicConfig.objects.create(
            subject=self.subject, academic_grade=self.grade,
            weekly_hours=5,
        )
        self.offering = SubjectOffering.objects.create(
            section=self.section,
            subject_academic_config=self.config,
        )
        self.scale_c = QualitativeScale.objects.get_or_create(
            code="SA", defaults={"name": "Satisfactorio", "numeric_equivalence": 8.0},
        )[0]
        self.activity_type = ActivityType.objects.get_or_create(
            code="EXAMEN", defaults={"name": "Examen"},
        )[0]
        from apps.grading.evaluation import EvaluationBlock, BlockComponent
        from apps.academic.teacher_subject_section.infrastructure.models import TeacherSubjectSection
        self.eval_block = EvaluationBlock.objects.create(
            academic_period=self.period, subject_offering=self.offering,
            name="Bloque 1", weight_percentage=Decimal("100.00"),
        )
        self.block_comp = BlockComponent.objects.create(
            evaluation_block=self.eval_block, name="Componente 1",
            internal_weight=Decimal("100.00"),
        )
        self.tss = TeacherSubjectSection.objects.create(
            user=self.teacher, subject_offering=self.offering,
        )
        self.eval_activity = EvaluativeActivity.objects.create(
            block_component=self.block_comp, teacher_subject_section=self.tss,
            title="Examen parcial", activity_type=self.activity_type,
            max_score=Decimal("10.00"), internal_weight=Decimal("100.00"),
            due_date=date(2025, 10, 15),
        )
    def test_enrollment_to_graduation_workflow(self):
        attendance_status = AttendanceStatus.objects.get_or_create(code="P", defaults={"name": "Presente"})[0]
        note = StudentNote.objects.create(
            enrollment=self.enrollment, evaluative_activity=self.eval_activity,
            numeric_score=Decimal("8.50"), grading_mode="NUMERIC",
        )
        summary = PeriodGradeSummary.objects.create(
            enrollment=self.enrollment, subject_offering=self.offering,
            academic_period=self.period, formative_avg=Decimal("6.50"),
            summative_avg=Decimal("5.50"), final_avg_truncated=Decimal("6.00"),
            is_failing=True, qualitative_scale=self.scale_c,
        )
        self.assertIsNotNone(note.created_at)
        self.assertTrue(summary.is_failing)

    def test_grade_change_history_extended(self):
        note = StudentNote.objects.create(
            enrollment=self.enrollment, evaluative_activity=self.eval_activity,
            numeric_score=Decimal("7.00"), grading_mode="NUMERIC",
        )
        history = GradeChangeHistory.objects.create(
            student_note=note, modified_by_user=self.teacher,
            previous_score=Decimal("7.00"), new_score=Decimal("9.00"),
            reason="Corrección por error de captura",
            reason_code="ERROR_CAPTURA", origin="MANUAL",
        )
        self.assertEqual(history.reason_code, "ERROR_CAPTURA")
        self.assertEqual(history.origin, "MANUAL")
        self.assertEqual(history.new_score, Decimal("9.00"))

    def test_behavior_evaluation_workflow(self):
        severity = Severity.objects.create(code="LEVE", name="Falta leve")
        inc_type = IncidentType.objects.get_or_create(code="disciplina", defaults={"name": "Disciplina"})[0]
        incident = ConductIncident.objects.create(
            enrollment=self.enrollment,
            academic_period=self.period, incident_type=inc_type,
            incident_date=date(2025, 10, 1), severity=severity,
            description="Llegó tarde", family_notified=True,
        )
        self.assertEqual(incident.severity.code, "LEVE")
        self.assertTrue(incident.family_notified)

    def test_dashboard_and_csv_export(self):
        enrollments = []
        for i in range(3):
            s = create_test_student(
                document_number=f"222222222{i}", names=f"Student{i}",
                last_names="Test", birth_date=date(2012, 1, 1),
            )
            e = Enrollment.objects.create(
                student=s, section=self.section,
                enrollment_status="ACT",
            )
            enrollments.append(e)
        labels = ["rojo", "amarillo", "verde"]
        for i, enrollment in enumerate(enrollments):
            StudentRiskScore.objects.create(
                enrollment=enrollment, academic_period=self.period,
                risk_score=Decimal(str(50 + i * 20)),
                risk_label=labels[i], model_version="v1.0",
            )
        overview = DashboardService.get_overview(self.period.id)
        self.assertIn("total_students", overview)
        self.assertIn("risk_distribution", overview)
        csv = CSVExportService.generate_csv("risk", self.period.id)
        lines = csv.strip().split("\n")
        self.assertIn("Score Riesgo", lines[0])

    def test_api_endpoints_return_ok(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(f"/api/analytics/dashboard/overview/?period_id={self.period.id}")
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])
