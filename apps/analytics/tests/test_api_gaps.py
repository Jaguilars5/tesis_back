"""
Tests de integración y unitarios adicionales para cubrir los vacíos (gaps) del módulo analytics.

Prueba el control de acceso RBAC, respuestas de vistas (ViewSets) y la acción custom `mark_attended`.
"""

from datetime import date
from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.iam.models import Permission, Role, RolePermission, User, UserRole
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.core.constants.permissions import analytics

from apps.analytics.models import (
    RiskFactor, StudentFeatureSnapshot, StudentRiskFactor, StudentRiskScore, EarlyAlert,
)
from apps.analytics.models.early_alert import AlertTypeChoices, UrgencyLevelChoices
from apps.academic.models import AcademicPeriod, PeriodType
from apps.institutions.models import SchoolYear, AcademicGrade, AcademicLevel, AcademicSublevel, Section
from apps.students.models import Enrollment


class AnalyticsAPIGapsTest(TestCase):
    """Suite de pruebas de integración para cubrir brechas en la API de Analytics."""

    def setUp(self):
        self.client = APIClient()

        # 1. Configuración básica académica
        self.school_year = SchoolYear.objects.create(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
        )
        self.academic_level = AcademicLevel.objects.create(name="Primaria")
        self.academic_sublevel = AcademicSublevel.objects.create(
            academic_level=self.academic_level, name="Básica"
        )
        self.academic_grade = AcademicGrade.objects.create(
            academic_sublevel=self.academic_sublevel,
            name="7"        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            academic_grade=self.academic_grade,
            parallel="A",
            capacity=30,
        )
        self.period = AcademicPeriod.objects.create(
            school_year=self.school_year,
            name="P1",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
        )

        self.student = create_test_student(
            document_number="0912345678",
            names="Juan",
            last_names="Lopez",
            birth_date=date(2010, 1, 1),
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            section=self.section,
            enrollment_status="ACT",
        )

        # 2. Creación de Usuarios
        self.admin = create_test_user(
            email="admin_analytics@test.com",
            dni="8888888881",
            names="Admin",
            last_names="Analytics",
            is_superuser=True,
        )

        self.authorized_user = create_test_user(
            email="auth_analytics@test.com",
            dni="8888888882",
            names="Authorized",
            last_names="Analytics",
            is_superuser=False,
        )

        self.noperm_user = create_test_user(
            email="noperm_analytics@test.com",
            dni="8888888883",
            names="NoPerm",
            last_names="Analytics",
            is_superuser=False,
        )

        # 3. Permisos y Rol
        self.role_authorized = Role.objects.create(name="Authorized Role", code="ADMIN")
        UserRole.objects.create(user=self.authorized_user, role=self.role_authorized)

        self.perm_view_score = Permission.objects.create(
            code=analytics.VIEW_RISK_SCORE, module="analytics", description="Ver riesgo"
        )
        self.perm_view_snapshot = Permission.objects.create(
            code=analytics.VIEW_FEATURE_SNAPSHOT, module="analytics", description="Ver snapshot"
        )
        self.perm_view_factor = Permission.objects.create(
            code=analytics.VIEW_RISK_FACTOR, module="analytics", description="Ver factor"
        )
        self.perm_view_student_factor = Permission.objects.create(
            code=analytics.VIEW_STUDENT_RISK_FACTOR, module="analytics", description="Ver factor estudiante"
        )
        self.perm_view_alert = Permission.objects.create(
            code=analytics.VIEW_EARLY_ALERT, module="analytics", description="Ver alerta"
        )
        self.perm_create_alert = Permission.objects.create(
            code=analytics.CREATE_EARLY_ALERT, module="analytics", description="Crear alerta"
        )
        self.perm_update_alert = Permission.objects.create(
            code=analytics.UPDATE_EARLY_ALERT, module="analytics", description="Actualizar alerta"
        )
        self.perm_delete_alert = Permission.objects.create(
            code=analytics.DELETE_EARLY_ALERT, module="analytics", description="Eliminar alerta"
        )

        for perm in [
            self.perm_view_score, self.perm_view_snapshot, self.perm_view_factor,
            self.perm_view_student_factor, self.perm_view_alert, self.perm_create_alert,
            self.perm_update_alert, self.perm_delete_alert
        ]:
            RolePermission.objects.create(role=self.role_authorized, permission=perm)

        # 4. Instancias de prueba en base de datos
        self.risk_factor = RiskFactor.objects.create(
            code="ABSENTEEISM", name="Ausentismo Alto", description="El estudiante falta mucho"
        )
        self.risk_score = StudentRiskScore.objects.create(
            enrollment=self.enrollment,
            academic_period=self.period,
            risk_score=Decimal("75.00"),
            risk_label="alto",
            model_version="v1_rules",
        )
        self.student_risk_factor = StudentRiskFactor.objects.create(
            student_risk_score=self.risk_score,
            risk_factor=self.risk_factor,
            contribution_weight=Decimal("100.00"),
        )
        self.feature_snapshot = StudentFeatureSnapshot.objects.create(
            enrollment=self.enrollment,
            academic_period=self.period,
            attendance_rate=Decimal("65.50"),
            consecutive_absences_max=5,
            tardiness_count=3,
            formative_avg_normalized=Decimal("5.50"),
            summative_avg_normalized=Decimal("6.00"),
            failing_subjects_count=2,
            conduct_score=Decimal("7.00"),
        )
        self.early_alert = EarlyAlert.objects.create(
            enrollment=self.enrollment,
            academic_period=self.period,
            alert_type=AlertTypeChoices.DROPOUT_RISK,
            description="Alto riesgo de deserción por ausentismo y notas bajas",
            urgency_level=UrgencyLevelChoices.HIGH,
            attended=False,
        )

    def test_student_risk_scores_api(self):
        """Prueba permisos RBAC y respuestas para StudentRiskScoreViewSet."""
        # Con permisos
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/analytics/student-risk-scores/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["ok"])
        results = response.json()["data"]["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["risk_label"], "alto")

        # Sin permisos -> 403
        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/analytics/student-risk-scores/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_feature_snapshots_api(self):
        """Prueba permisos RBAC y respuestas para StudentFeatureSnapshotViewSet."""
        # Con permisos
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/analytics/feature-snapshots/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["ok"])
        results = response.json()["data"]["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(float(results[0]["attendance_rate"]), 65.50)

        # Sin permisos -> 403
        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/analytics/feature-snapshots/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_risk_factors_api(self):
        """Prueba de solo lectura y RBAC para RiskFactorViewSet."""
        # Con permisos
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/analytics/risk-factors/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["ok"])
        results = response.json()["data"]["results"]
        self.assertTrue(any(x["code"] == "ABSENTEEISM" for x in results))

        # Intentar POST -> 405 Method Not Allowed (Superusuario)
        self.client.force_authenticate(user=self.admin)
        response = self.client.post("/api/analytics/risk-factors/", {"code": "TEST", "name": "Test"})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Sin permisos -> 403
        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/analytics/risk-factors/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_risk_factors_api(self):
        """Prueba de solo lectura y RBAC para StudentRiskFactorViewSet."""
        # Con permisos
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/analytics/student-risk-factors/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["ok"])
        results = response.json()["data"]["results"]
        self.assertTrue(any(x["risk_factor_name"] == "Ausentismo Alto" for x in results))

        # Intentar POST -> 405 Method Not Allowed (Superusuario)
        self.client.force_authenticate(user=self.admin)
        response = self.client.post("/api/analytics/student-risk-factors/", {"student_risk_score": self.risk_score.id})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Sin permisos -> 403
        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/analytics/student-risk-factors/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_early_alerts_rbac_and_custom_action(self):
        """Prueba permisos RBAC, CRUD y acción mark_attended para EarlyAlertViewSet."""
        # Con permisos
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/analytics/early-alerts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["ok"])
        results = response.json()["data"]["results"]
        self.assertEqual(len(results), 1)

        # Crear alerta
        data = {
            "enrollment": self.enrollment.id,
            "academic_period": self.period.id,
            "alert_type": AlertTypeChoices.FAILING_GRADES,
            "description": "Notas rojas",
            "urgency_level": UrgencyLevelChoices.MEDIUM,
        }
        response = self.client.post("/api/analytics/early-alerts/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Probar acción custom: mark_attended
        response_actions_data = {
            "response_actions": "Reunión con los padres programada para mañana",
        }
        response_action = self.client.post(
            f"/api/analytics/early-alerts/{self.early_alert.id}/mark_attended/",
            response_actions_data,
            format="json"
        )
        self.assertEqual(response_action.status_code, status.HTTP_200_OK)
        self.assertTrue(response_action.json()["ok"])
        self.assertEqual(response_action.json()["data"]["attended"], True)
        self.assertEqual(
            response_action.json()["data"]["response_actions"],
            "Reunión con los padres programada para mañana"
        )

        # Sin permisos -> 403
        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/analytics/early-alerts/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
