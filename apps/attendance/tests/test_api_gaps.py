from datetime import date
from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.accounts.models import Permission, Role, RolePermission, UserRole
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.core.constants.permissions import attendance as perm_constants

from apps.attendance.models import (
    Attendance, AttendanceStatus, IncidentType, ConductIncident,
    SocioemotionalSkill, SkillEvaluation, BehaviorEvaluation
)
from apps.grading.models import QualitativeScale
from apps.academic.models import Academic_Period, Subject, SubjectAcademicConfig, SubjectOffering, Teacher_Subject_Section
from apps.institutions.models import School_Year, AcademicGrade, AcademicLevel, Section
from apps.students.models import Enrollment, EnrollmentStatus


class AttendanceAPIGapsTest(TestCase):
    """Suite de pruebas de integración para cubrir brechas de API y seguridad en el módulo de asistencia."""

    def setUp(self):
        self.client = APIClient()

        # 1. Estructura académica básica
        self.school_year = School_Year.objects.create(
            name="2025",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
        )
        self.academic_period = Academic_Period.objects.create(
            school_year=self.school_year,
            name="P1",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
        )
        self.academic_level = AcademicLevel.objects.create(name="Primaria")
        self.academic_grade = AcademicGrade.objects.create(
            academic_level=self.academic_level,
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

        # 2. Configuración de Usuarios de Prueba (user_type="ADMIN" para omitir RLS)
        self.admin = create_test_user(
            email="admin_att@test.com",
            dni="8888888871",
            names="Admin",
            last_names="Attendance",
            is_superuser=True,
        )
        self.authorized_user = create_test_user(
            email="auth_att@test.com",
            dni="8888888872",
            names="Authorized",
            last_names="Attendance",
            user_type="ADMIN",
            is_superuser=False,
        )
        self.noperm_user = create_test_user(
            email="noperm_att@test.com",
            dni="8888888873",
            names="NoPerm",
            last_names="Attendance",
            user_type="ADMIN",
            is_superuser=False,
        )

        # 3. Configuración de Carga Docente
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
        self.teacher_subject_section = Teacher_Subject_Section.objects.create(
            user=self.authorized_user,
            subject_offering=offering,
        )

        # 4. Roles y Permisos RBAC
        self.role_authorized = Role.objects.create(name="Authorized Attendance Role")
        UserRole.objects.create(user=self.authorized_user, role=self.role_authorized)

        # Sembrar todos los permisos de asistencia para el rol autorizado
        permissions_codes = [
            perm_constants.VIEW_ATTENDANCE, perm_constants.CREATE_ATTENDANCE,
            perm_constants.UPDATE_ATTENDANCE, perm_constants.DELETE_ATTENDANCE,
            perm_constants.VIEW_CONDUCT_INCIDENT, perm_constants.CREATE_CONDUCT_INCIDENT,
            perm_constants.UPDATE_CONDUCT_INCIDENT, perm_constants.DELETE_CONDUCT_INCIDENT,
            perm_constants.VIEW_BEHAVIOR_EVALUATION, perm_constants.CREATE_BEHAVIOR_EVALUATION,
            perm_constants.UPDATE_BEHAVIOR_EVALUATION, perm_constants.DELETE_BEHAVIOR_EVALUATION,
            perm_constants.VIEW_INCIDENT_TYPE, perm_constants.CREATE_INCIDENT_TYPE,
            perm_constants.UPDATE_INCIDENT_TYPE, perm_constants.DELETE_INCIDENT_TYPE,
            perm_constants.VIEW_SOCIOEMOTIONAL_SKILL, perm_constants.CREATE_SOCIOEMOTIONAL_SKILL,
            perm_constants.UPDATE_SOCIOEMOTIONAL_SKILL, perm_constants.DELETE_SOCIOEMOTIONAL_SKILL,
            perm_constants.VIEW_SKILL_EVALUATION, perm_constants.CREATE_SKILL_EVALUATION,
            perm_constants.UPDATE_SKILL_EVALUATION, perm_constants.DELETE_SKILL_EVALUATION,
            perm_constants.VIEW_ATTENDANCE_STATUS, perm_constants.CREATE_ATTENDANCE_STATUS,
            perm_constants.UPDATE_ATTENDANCE_STATUS, perm_constants.DELETE_ATTENDANCE_STATUS,
        ]

        for code in permissions_codes:
            perm_obj, _ = Permission.objects.get_or_create(
                code=code, module="attendance", defaults={"description": f"Permiso {code}"}
            )
            RolePermission.objects.create(role=self.role_authorized, permission=perm_obj)

        # 5. Creación de Datos de Prueba en la BD
        self.qualitative_scale = QualitativeScale.objects.create(
            code="SE",
            description="Superior",
            numeric_equivalence=Decimal("10.00"),
        )
        self.attendance_status = AttendanceStatus.objects.create(
            code="P",
            name="Presente",
            tipo="POSITIVO",
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
            active=True,
        )

        self.attendance = Attendance.objects.create(
            enrollment=self.enrollment,
            teacher_subject_section=self.teacher_subject_section,
            academic_period=self.academic_period,
            attendance_status=self.attendance_status,
            attendance_date=date(2025, 2, 1),
            absence_type="none",
        )
        self.conduct_incident = ConductIncident.objects.create(
            enrollment=self.enrollment,
            reported_by_user=self.authorized_user,
            academic_period=self.academic_period,
            incident_type=self.incident_type,
            incident_date=date(2025, 2, 1),
            severity=1,
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

    def test_attendance_api_rbac_and_crud(self):
        """Valida seguridad RBAC y operaciones sobre AttendanceViewSet."""
        # 1. Petición Autorizada (Listar)
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/attendance/attendances/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        results = response.data["data"]["results"]
        self.assertEqual(len(results), 1)

        # 2. Petición Autorizada (Crear)
        new_status = AttendanceStatus.objects.create(code="FJ", name="Falta Justificada", tipo="NEGATIVO")
        post_data = {
            "enrollment": self.enrollment.id,
            "teacher_subject_section": self.teacher_subject_section.id,
            "academic_period": self.academic_period.id,
            "attendance_status": new_status.id,
            "attendance_date": "2025-02-02",
            "absence_type": "justified",
        }
        response = self.client.post("/api/attendance/attendances/", post_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 3. Petición Autorizada (Eliminar)
        response = self.client.delete(f"/api/attendance/attendances/{self.attendance.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # 4. Petición No Autorizada (Acceso bloqueado)
        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/attendance/attendances/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_conduct_incident_api_rbac_and_crud(self):
        """Valida seguridad RBAC y operaciones sobre ConductIncidentViewSet."""
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/attendance/conduct-incidents/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["data"]["results"]
        self.assertEqual(len(results), 1)

        # Crear
        post_data = {
            "enrollment": self.enrollment.id,
            "reported_by_user": self.authorized_user.id,
            "academic_period": self.academic_period.id,
            "incident_type": self.incident_type.id,
            "incident_date": "2025-02-02",
            "severity": 2,
        }
        response = self.client.post("/api/attendance/conduct-incidents/", post_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # No Autorizado
        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/attendance/conduct-incidents/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_behavior_evaluation_api_rbac_and_crud(self):
        """Valida seguridad RBAC y operaciones sobre BehaviorEvaluationViewSet."""
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/attendance/behavior-evaluations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["data"]["results"]
        self.assertEqual(len(results), 1)

        # Crear
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
        response = self.client.post("/api/attendance/behavior-evaluations/", post_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # No Autorizado
        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/attendance/behavior-evaluations/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_incident_type_api_rbac_and_crud(self):
        """Valida seguridad RBAC y operaciones sobre IncidentTypeViewSet."""
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/attendance/incident-types/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["data"]["results"]
        self.assertEqual(len(results), 1)

        # Crear
        post_data = {
            "code": "GRAVE_FALTA",
            "name": "Falta Muy Grave",
            "description": "Faltas críticas al reglamento escolar",
        }
        response = self.client.post("/api/attendance/incident-types/", post_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # No Autorizado
        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/attendance/incident-types/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_socioemotional_skill_api_rbac_and_crud(self):
        """Valida seguridad RBAC y operaciones sobre SocioemotionalSkillViewSet."""
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/attendance/socioemotional-skills/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["data"]["results"]
        self.assertEqual(len(results), 1)

        # Crear
        post_data = {
            "code": "RESILIENCIA",
            "name": "Resiliencia",
            "description": "Superación de situaciones difíciles",
            "active": True,
        }
        response = self.client.post("/api/attendance/socioemotional-skills/", post_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # No Autorizado
        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/attendance/socioemotional-skills/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_skill_evaluation_api_rbac_and_crud(self):
        """Valida seguridad RBAC y operaciones sobre SkillEvaluationViewSet."""
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/attendance/skill-evaluations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["data"]["results"]
        self.assertEqual(len(results), 1)

        # Crear
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
        response = self.client.post("/api/attendance/skill-evaluations/", post_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # No Autorizado
        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/attendance/skill-evaluations/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_attendance_status_api_rbac_and_crud(self):
        """Valida seguridad RBAC y operaciones sobre AttendanceStatusViewSet."""
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/attendance/attendance-statuses/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["data"]["results"]
        self.assertEqual(len(results), 1)

        # Crear
        post_data = {
            "code": "A",
            "name": "Ausente",
            "tipo": "NEGATIVO",
        }
        response = self.client.post("/api/attendance/attendance-statuses/", post_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # No Autorizado
        self.client.force_authenticate(user=self.noperm_user)
        response = self.client.get("/api/attendance/attendance-statuses/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
