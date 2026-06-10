from datetime import date
from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.iam.models import Permission, Role, RolePermission, UserRole
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.core.constants.permissions import behavior

from apps.behavior.models import (
    ConductIncident, SocioemotionalSkill,
    SkillEvaluation, BehaviorEvaluation, IncidentType, Severity,
    SocioemotionalArea, DevelopmentLevel,
)
from apps.grading.models import QualitativeScale
from apps.academic.models import AcademicPeriod, Subject, SubjectAcademicConfig, SubjectOffering, TeacherSubjectSection, PeriodType
from apps.institutions.models import SchoolYear, AcademicGrade, AcademicLevel, AcademicSublevel, Section
from apps.students.models import Enrollment, EnrollmentStatus


class BehaviorAPIGapsTest(TestCase):
    """Suite de pruebas de integración para cubrir brechas de API y seguridad en el módulo de comportamiento."""

    def setUp(self):
        self.client = APIClient()

        self.school_year = SchoolYear.objects.create(
            name="2025",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
        )
        self.academic_period = AcademicPeriod.objects.create(
            school_year=self.school_year,
            name="P1",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
        )
        self.academic_level = AcademicLevel.objects.create(name="Primaria")
        self.academic_sublevel = AcademicSublevel.objects.create(
            academic_level=self.academic_level, name="Básica"
        )
        self.academic_grade = AcademicGrade.objects.create(
            academic_sublevel=self.academic_sublevel,
            name="7",
            sequence_order=1,
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            academic_grade=self.academic_grade,
            parallel="A",
            capacity=30,
        )
        self.subject = Subject.objects.create(
            name="Matemática",
            code="MAT-7A",
        )
        self.student = create_test_student(
            document_number="0912345678",
            names="Juan",
            last_names="Lopez",
            birth_date=date(2010, 1, 1),
        )
        enr_status, _ = EnrollmentStatus.objects.get_or_create(
            code="ACT", defaults={"name": "Activa"}
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            section=self.section,
            school_year=self.school_year,
            enrollment_status=enr_status,
        )

        self.admin = create_test_user(
            email="admin_beh@test.com",
            dni="8888888871",
            names="Admin",
            last_names="Behavior",
            is_superuser=True,
        )
        self.authorized_user = create_test_user(
            email="auth_beh@test.com",
            dni="8888888872",
            names="Authorized",
            last_names="Behavior",
            is_superuser=False,
        )
        self.noperm_user = create_test_user(
            email="noperm_beh@test.com",
            dni="8888888873",
            names="NoPerm",
            last_names="Behavior",
            is_superuser=False,
        )

        subj_config = SubjectAcademicConfig.objects.create(
            subject=self.subject,
            academic_grade=self.academic_grade,
            weekly_hours=5,
            pedagogical_order=1,
        )
        offering = SubjectOffering.objects.create(
            school_year=self.school_year,
            section=self.section,
            subject_academic_config=subj_config,
        )
        self.teacher_subject_section = TeacherSubjectSection.objects.create(
            user=self.authorized_user,
            subject_offering=offering,
        )

        self.role_authorized = Role.objects.create(name="Authorized Behavior Role", code="ADMIN")
        UserRole.objects.create(user=self.authorized_user, role=self.role_authorized)

        permissions_codes = [
            behavior.VIEW_CONDUCT_INCIDENT, behavior.CREATE_CONDUCT_INCIDENT,
            behavior.UPDATE_CONDUCT_INCIDENT, behavior.DELETE_CONDUCT_INCIDENT,
            behavior.VIEW_BEHAVIOR_EVALUATION, behavior.CREATE_BEHAVIOR_EVALUATION,
            behavior.UPDATE_BEHAVIOR_EVALUATION, behavior.DELETE_BEHAVIOR_EVALUATION,
            behavior.VIEW_INCIDENT_TYPE, behavior.CREATE_INCIDENT_TYPE,
            behavior.UPDATE_INCIDENT_TYPE, behavior.DELETE_INCIDENT_TYPE,
            behavior.VIEW_SOCIOEMOTIONAL_SKILL, behavior.CREATE_SOCIOEMOTIONAL_SKILL,
            behavior.UPDATE_SOCIOEMOTIONAL_SKILL, behavior.DELETE_SOCIOEMOTIONAL_SKILL,
            behavior.VIEW_SKILL_EVALUATION, behavior.CREATE_SKILL_EVALUATION,
            behavior.UPDATE_SKILL_EVALUATION, behavior.DELETE_SKILL_EVALUATION,
            behavior.VIEW_DIAGNOSTIC_EVALUATION, behavior.CREATE_DIAGNOSTIC_EVALUATION,
            behavior.UPDATE_DIAGNOSTIC_EVALUATION, behavior.DELETE_DIAGNOSTIC_EVALUATION,
        ]

        for code in permissions_codes:
            perm_obj, _ = Permission.objects.get_or_create(
                code=code, module="behavior", defaults={"description": f"Permiso {code}"}
            )
            RolePermission.objects.create(role=self.role_authorized, permission=perm_obj)

        self.qualitative_scale = QualitativeScale.objects.create(
            code="SE",
            description="Superior",
            numeric_equivalence=Decimal("10.00"),
        )
        self.incident_type = IncidentType.objects.create(
            code="INDISCIPLINA",
            name="Falta Disciplinaria",
            description="Llegar tarde o perturbar clase",
        )
        self.socioemotional_skill = SocioemotionalSkill.objects.create(
            code="EMPATIA",
            name="Empatía",
            description="Habilidad de ponerse en el lugar del otro",
            is_active=True,
        )
        self.severity_leve = Severity.objects.create(
            code="LEVE", name="Falta leve", numeric_level=1,
        )
        self.severity_moderada = Severity.objects.create(
            code="MODERADA", name="Falta moderada", numeric_level=2,
        )
        self.socioemotional_area = SocioemotionalArea.objects.create(
            code="RELACIONES", name="Relaciones interpersonales",
        )
        self.development_level = DevelopmentLevel.objects.create(
            code="LOGRADO", name="Logrado",
        )

        self.conduct_incident = ConductIncident.objects.create(
            enrollment=self.enrollment,
            reported_by_user=self.authorized_user,
            academic_period=self.academic_period,
            incident_type=self.incident_type,
            incident_date=date(2025, 2, 1),
            severity=self.severity_leve,
        )
        self.skill_evaluation = SkillEvaluation.objects.create(
            enrollment=self.enrollment,
            academic_period=self.academic_period,
            socioemotional_skill=self.socioemotional_skill,
            qualitative_scale=self.qualitative_scale,
        )
        self.behavior_evaluation = BehaviorEvaluation.objects.create(
            enrollment=self.enrollment,
            academic_period=self.academic_period,
            calculated_scale=self.qualitative_scale,
        )

    def test_conduct_incident_api_rbac_and_crud(self):
        """Valida seguridad RBAC y operaciones sobre ConductIncidentViewSet."""
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/behavior/conduct-incidents/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()["data"]["results"]
        self.assertEqual(len(results), 1)

        post_data = {
            "enrollment": self.enrollment.id,
            "reported_by_user": self.authorized_user.id,
            "academic_period": self.academic_period.id,
            "incident_type": self.incident_type.id,
            "incident_date": "2025-02-02",
            "severity": self.severity_moderada.id,
        }
        response = self.client.post("/api/behavior/conduct-incidents/", post_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/behavior/conduct-incidents/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_behavior_evaluation_api_rbac_and_crud(self):
        """Valida seguridad RBAC y operaciones sobre BehaviorEvaluationViewSet."""
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/behavior/behavior-evaluations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()["data"]["results"]
        self.assertEqual(len(results), 1)

        student2 = create_test_student(
            document_number="0912345679",
            names="Maria",
            last_names="Zambrano",
            birth_date=date(2010, 5, 5),
        )
        enr_status2 = EnrollmentStatus.objects.get(code="ACT")
        enrollment2 = Enrollment.objects.create(
            student=student2,
            section=self.section,
            school_year=self.school_year,
            enrollment_status=enr_status2,
        )
        post_data = {
            "enrollment": enrollment2.id,
            "academic_period": self.academic_period.id,
            "calculated_scale": self.qualitative_scale.id,
        }
        response = self.client.post("/api/behavior/behavior-evaluations/", post_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/behavior/behavior-evaluations/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_incident_type_api_rbac_and_crud(self):
        """Valida seguridad RBAC y operaciones sobre IncidentTypeViewSet."""
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/behavior/incident-types/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()["data"]["results"]
        self.assertEqual(len(results), 1)

        post_data = {
            "code": "GRAVE_FALTA",
            "name": "Falta Muy Grave",
            "description": "Faltas críticas al reglamento escolar",
        }
        response = self.client.post("/api/behavior/incident-types/", post_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/behavior/incident-types/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_socioemotional_skill_api_rbac_and_crud(self):
        """Valida seguridad RBAC y operaciones sobre SocioemotionalSkillViewSet."""
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/behavior/socioemotional-skills/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()["data"]["results"]
        self.assertEqual(len(results), 1)

        post_data = {
            "code": "RESILIENCIA",
            "name": "Resiliencia",
            "description": "Superación de situaciones difíciles",
            "active": True,
        }
        response = self.client.post("/api/behavior/socioemotional-skills/", post_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/behavior/socioemotional-skills/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_skill_evaluation_api_rbac_and_crud(self):
        """Valida seguridad RBAC y operaciones sobre SkillEvaluationViewSet."""
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/behavior/skill-evaluations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()["data"]["results"]
        self.assertEqual(len(results), 1)

        student2 = create_test_student(
            document_number="0912345679",
            names="Maria",
            last_names="Zambrano",
            birth_date=date(2010, 5, 5),
        )
        enr_status2 = EnrollmentStatus.objects.get(code="ACT")
        enrollment2 = Enrollment.objects.create(
            student=student2,
            section=self.section,
            school_year=self.school_year,
            enrollment_status=enr_status2,
        )
        post_data = {
            "enrollment": enrollment2.id,
            "academic_period": self.academic_period.id,
            "socioemotional_skill": self.socioemotional_skill.id,
            "qualitative_scale": self.qualitative_scale.id,
        }
        response = self.client.post("/api/behavior/skill-evaluations/", post_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/behavior/skill-evaluations/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_diagnostic_evaluation_api_rbac_and_crud(self):
        """Valida seguridad RBAC y operaciones sobre DiagnosticEvaluationViewSet."""
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/behavior/diagnostic-evaluations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["ok"])

        data = {
            "enrollment": self.enrollment.id,
            "academic_period": self.academic_period.id,
            "applied_by_user": self.authorized_user.id,
            "socioemotional_area": self.socioemotional_area.id,
            "findings_description": "Excelente liderazgo",
            "development_level": self.development_level.id,
            "application_date": "2025-02-20",
        }
        response = self.client.post("/api/behavior/diagnostic-evaluations/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/behavior/diagnostic-evaluations/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)