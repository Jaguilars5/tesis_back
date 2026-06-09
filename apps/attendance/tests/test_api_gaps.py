from datetime import date
from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.iam.models import Permission, Role, RolePermission, UserRole
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.core.constants.permissions import attendance as perm_constants

from apps.attendance.models import Attendance, AbsenceType
from apps.attendance.models import AttendanceStatus
from apps.grading.models import QualitativeScale
from apps.academic.models import AcademicPeriod, Subject, SubjectAcademicConfig, SubjectOffering, TeacherSubjectSection
from apps.institutions.models import SchoolYear, AcademicGrade, AcademicLevel, AcademicSublevel, Section
from apps.students.models import Enrollment, EnrollmentStatus


class AttendanceAPIGapsTest(TestCase):
    """Suite de pruebas de integración para cubrir brechas de API y seguridad en el módulo de asistencia."""

    def setUp(self):
        self.client = APIClient()

        # 1. Estructura académica básica
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
            is_superuser=False,
        )
        self.noperm_user = create_test_user(
            email="noperm_att@test.com",
            dni="8888888873",
            names="NoPerm",
            last_names="Attendance",
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
        self.teacher_subject_section = TeacherSubjectSection.objects.create(
            user=self.authorized_user,
            subject_offering=offering,
        )

        # 4. Roles y Permisos RBAC
        self.role_authorized = Role.objects.create(name="Authorized Attendance Role", code="ADMIN")
        UserRole.objects.create(user=self.authorized_user, role=self.role_authorized)

        permissions_codes = [
            perm_constants.VIEW_ATTENDANCE, perm_constants.CREATE_ATTENDANCE,
            perm_constants.UPDATE_ATTENDANCE, perm_constants.DELETE_ATTENDANCE,
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

        self.absence_type_none = AbsenceType.objects.create(
            code="none", name="Ninguno"
        )
        self.absence_type_justified = AbsenceType.objects.create(
            code="justified", name="Justificado"
        )
        self.absence_type_unjustified = AbsenceType.objects.create(
            code="unjustified", name="Injustificado"
        )

        self.attendance = Attendance.objects.create(
            enrollment=self.enrollment,
            teacher_subject_section=self.teacher_subject_section,
            academic_period=self.academic_period,
            attendance_status=self.attendance_status,
            attendance_date=date(2025, 2, 1),
            absence_type=self.absence_type_none,
        )

    def test_attendance_api_rbac_and_crud(self):
        """Valida seguridad RBAC y operaciones sobre AttendanceViewSet."""
        # 1. Petición Autorizada (Listar)
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/attendance/attendances/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["ok"])
        results = response.json()["data"]["results"]
        self.assertEqual(len(results), 1)

        # 2. Petición Autorizada (Crear)
        new_status = AttendanceStatus.objects.create(code="FJ", name="Falta Justificada", tipo="NEGATIVO")
        post_data = {
            "enrollment": self.enrollment.id,
            "teacher_subject_section": self.teacher_subject_section.id,
            "academic_period": self.academic_period.id,
            "attendance_status": new_status.id,
            "attendance_date": "2025-02-02",
            "absence_type": self.absence_type_justified.id,
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

    def test_attendance_status_api_rbac_and_crud(self):
        """Valida seguridad RBAC y operaciones sobre AttendanceStatusViewSet."""
        self.client.force_authenticate(user=self.authorized_user)
        response = self.client.get("/api/attendance/attendance-statuses/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()["data"]["results"]
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
