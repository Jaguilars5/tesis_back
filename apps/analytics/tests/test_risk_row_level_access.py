from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.academic.academic_period import AcademicPeriod
from apps.academic.subject import Subject
from apps.academic.subject_academic_config import SubjectAcademicConfig
from apps.academic.subject_offering import SubjectOffering
from apps.academic.teacher_subject_section import TeacherSubjectSection
from apps.analytics.student_risk.infrastructure.models import (
    RiskFactor,
    StudentFeatureSnapshot,
    StudentRiskFactor,
    StudentRiskScore,
)
from apps.core.tests.helpers import create_test_student, create_test_user
from apps.iam.models import Permission, Role, RolePermission, UserRole
from apps.institutions.models import (
    AcademicGrade,
    AcademicLevel,
    AcademicSublevel,
    SchoolYear,
    Section,
)
from apps.students.models import Enrollment, Kinship, StudentRepresentative


class RiskRowLevelAccessTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        for code in (
            "analytics.view_risk_score",
            "analytics.view_feature_snapshot",
            "analytics.view_student_risk_factor",
            "analytics.create_student_risk_factor",
        ):
            Permission.objects.create(code=code, module="analytics")

        self.student_role = self._role(
            "ESTUDIANTE",
            [
                "analytics.view_risk_score",
                "analytics.view_feature_snapshot",
                "analytics.view_student_risk_factor",
            ],
        )
        self.rep_role = self._role(
            "REPRESENTANTE",
            [
                "analytics.view_risk_score",
                "analytics.view_feature_snapshot",
                "analytics.view_student_risk_factor",
            ],
        )
        self.teacher_role = self._role(
            "DOCENTE",
            [
                "analytics.view_risk_score",
                "analytics.view_feature_snapshot",
                "analytics.view_student_risk_factor",
            ],
        )

        self.school_year = SchoolYear.objects.create(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
        )
        self.period = AcademicPeriod.objects.create(
            school_year=self.school_year,
            name="P1",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 6, 30),
        )
        level = AcademicLevel.objects.create(name="Basica")
        sublevel = AcademicSublevel.objects.create(name="Superior", academic_level=level)
        grade = AcademicGrade.objects.create(name="Octavo", academic_sublevel=sublevel)
        self.section_a = Section.objects.create(
            school_year=self.school_year,
            academic_grade=grade,
            parallel="A",
            capacity=30,
        )
        self.section_b = Section.objects.create(
            school_year=self.school_year,
            academic_grade=grade,
            parallel="B",
            capacity=30,
        )
        subject = Subject.objects.create(name="Matematica", code="MAT")
        config = SubjectAcademicConfig.objects.create(
            subject=subject,
            academic_grade=grade,
            weekly_hours=4,
        )
        offering_a = SubjectOffering.objects.create(
            section=self.section_a,
            subject_academic_config=config,
        )
        SubjectOffering.objects.create(
            section=self.section_b,
            subject_academic_config=config,
        )

        self.teacher = create_test_user(
            email="teacher@test.com",
            dni="1000000001",
            names="Docente",
            last_names="Uno",
        )
        UserRole.objects.create(user=self.teacher, role=self.teacher_role)
        TeacherSubjectSection.objects.create(
            user=self.teacher,
            subject_offering=offering_a,
            is_active=True,
        )

        self.student_1 = create_test_student(
            "2000000001",
            names="Estudiante",
            last_names="Uno",
            student_code="S001",
        )
        self.student_2 = create_test_student(
            "2000000002",
            names="Estudiante",
            last_names="Dos",
            student_code="S002",
        )
        UserRole.objects.create(user=self.student_1.user, role=self.student_role)
        UserRole.objects.create(user=self.student_2.user, role=self.student_role)
        self.enrollment_1 = Enrollment.objects.create(
            student=self.student_1,
            section=self.section_a,
            enrollment_status="ACT",
        )
        self.enrollment_2 = Enrollment.objects.create(
            student=self.student_2,
            section=self.section_b,
            enrollment_status="ACT",
        )

        self.representative = create_test_user(
            email="rep@test.com",
            dni="3000000001",
            names="Representante",
            last_names="Uno",
        )
        UserRole.objects.create(user=self.representative, role=self.rep_role)
        kinship = Kinship.objects.create(code="PADRE", name="Padre")
        StudentRepresentative.objects.create(
            student=self.student_1,
            user=self.representative,
            kinship=kinship,
            is_primary=True,
            is_active=True,
        )

        self.score_1 = StudentRiskScore.objects.create(
            enrollment=self.enrollment_1,
            academic_period=self.period,
            risk_score=Decimal("75.00"),
            risk_label="rojo",
            model_version="rules-v1",
        )
        self.score_2 = StudentRiskScore.objects.create(
            enrollment=self.enrollment_2,
            academic_period=self.period,
            risk_score=Decimal("20.00"),
            risk_label="verde",
            model_version="rules-v1",
        )
        StudentFeatureSnapshot.objects.create(
            enrollment=self.enrollment_1,
            academic_period=self.period,
            attendance_rate=Decimal("70.00"),
        )
        StudentFeatureSnapshot.objects.create(
            enrollment=self.enrollment_2,
            academic_period=self.period,
            attendance_rate=Decimal("95.00"),
        )
        factor = RiskFactor.objects.create(code="LOW_ATTENDANCE", name="Asistencia")
        self.student_factor_1 = StudentRiskFactor.objects.create(
            student_risk_score=self.score_1,
            risk_factor=factor,
            contribution_weight=Decimal("35.00"),
        )
        StudentRiskFactor.objects.create(
            student_risk_score=self.score_2,
            risk_factor=factor,
            contribution_weight=Decimal("10.00"),
        )

    def _role(self, code, permission_codes):
        role = Role.objects.create(name=code.title(), code=code)
        for permission_code in permission_codes:
            RolePermission.objects.create(
                role=role,
                permission=Permission.objects.get(code=permission_code),
            )
        return role

    def _results(self, response):
        data = response.json()["data"]
        return data["results"] if isinstance(data, dict) and "results" in data else data

    def test_teacher_only_views_scores_for_assigned_sections(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get("/api/analytics/student-risk-scores/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["id"] for item in self._results(response)], [self.score_1.id])

    def test_representative_only_views_represented_risk_data(self):
        self.client.force_authenticate(user=self.representative)

        score_response = self.client.get("/api/analytics/student-risk-scores/")
        snapshot_response = self.client.get("/api/analytics/feature-snapshots/")
        factor_response = self.client.get("/api/analytics/student-risk-factors/")

        self.assertEqual(score_response.status_code, status.HTTP_200_OK)
        self.assertEqual(snapshot_response.status_code, status.HTTP_200_OK)
        self.assertEqual(factor_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["id"] for item in self._results(score_response)],
            [self.score_1.id],
        )
        self.assertEqual(len(self._results(snapshot_response)), 1)
        self.assertEqual(
            [item["id"] for item in self._results(factor_response)],
            [self.student_factor_1.id],
        )

    def test_student_only_views_own_risk_data(self):
        self.client.force_authenticate(user=self.student_1.user)

        score_response = self.client.get("/api/analytics/student-risk-scores/")
        snapshot_response = self.client.get("/api/analytics/feature-snapshots/")

        self.assertEqual(score_response.status_code, status.HTTP_200_OK)
        self.assertEqual(snapshot_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["id"] for item in self._results(score_response)],
            [self.score_1.id],
        )
        self.assertEqual(len(self._results(snapshot_response)), 1)

    def test_representative_cannot_predict_for_other_enrollment(self):
        self.client.force_authenticate(user=self.representative)

        with patch(
            "apps.analytics.ml.annual_model.AnnualRiskModelTrainer.predict",
            return_value={"probability": 10, "risk_level": "bajo"},
        ):
            response = self.client.post(
                "/api/analytics/student-risk-scores/predict_annual_risk/",
                {
                    "enrollment_id": self.enrollment_2.id,
                    "academic_period_id": self.period.id,
                },
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_cannot_recalculate(self):
        self.client.force_authenticate(user=self.student_1.user)
        response = self.client.post(
            "/api/analytics/dashboard/recalculate_period/",
            {"academic_period_id": self.period.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
