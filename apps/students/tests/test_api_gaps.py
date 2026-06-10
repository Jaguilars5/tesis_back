"""
Tests de integración y unitarios adicionales para el módulo students.

Cubre brechas detectadas:
1. Pruebas de integración de APIs en ViewSets anteriormente no probados (EnrollmentViewSet, StudentRepresentativeViewSet).
2. Pruebas de acciones personalizadas críticas (withdraw, transfer, set_primary, unlink, by_section, by_student).
3. Pruebas de seguridad RBAC positivas y negativas.
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date

from apps.people.models import Person
from apps.iam.models import Role, User, Permission, UserRole, RolePermission
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.core.constants.permissions import students

from apps.students.models import Student, StudentRepresentative, Enrollment, EnrollmentStatus, WithdrawalReason
from apps.institutions.models import SchoolYear, AcademicGrade, AcademicLevel, AcademicSublevel, Section
from apps.students.services.enrollment_service import EnrollmentService


class StudentsSecurityAndAPITest(TestCase):
    """Tests de integración de APIs y control de accesos RBAC."""

    def setUp(self):
        self.client = APIClient()

        self.school_year = SchoolYear.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )
        self.level = AcademicLevel.objects.create(name="Primaria")
        self.sublevel = AcademicSublevel.objects.create(
            academic_level=self.level, code="BASICA", name="Básica"
        )
        self.grade = AcademicGrade.objects.create(
            academic_sublevel=self.sublevel, name="6to", sequence_order=6
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            academic_grade=self.grade,
            parallel="A",
            capacity=40,
        )
        self.student = create_test_student(
            document_number="1234567890",
            names="Juan",
            last_names="Perez",
            birth_date=date(2012, 5, 15),
        )

        # Crear permisos necesarios en BD
        self.view_student_perm = Permission.objects.create(
            code=students.VIEW_STUDENT, module="students", description="Ver estudiantes"
        )
        self.create_student_perm = Permission.objects.create(
            code=students.CREATE_STUDENT, module="students", description="Crear estudiantes"
        )
        self.view_enrollment_perm = Permission.objects.create(
            code=students.VIEW_ENROLLMENT, module="students", description="Ver matriculas"
        )
        self.create_enrollment_perm = Permission.objects.create(
            code=students.CREATE_ENROLLMENT, module="students", description="Crear matriculas"
        )
        self.withdraw_perm = Permission.objects.create(
            code=students.WITHDRAW_STUDENT, module="students", description="Retirar estudiante"
        )

        # Rol limitado con permiso de lectura de estudiantes
        self.limited_role = Role.objects.create(name="Student Limited", code="ST_LIM")
        RolePermission.objects.create(role=self.limited_role, permission=self.view_student_perm)

        # Usuario limitado (no superusuario)
        self.limited_user = create_test_user(
            email="st_lim@example.com",
            dni="DNI-ST-LIM",
            is_superuser=False,
        )
        UserRole.objects.create(user=self.limited_user, role=self.limited_role)

        # Usuario sin permisos
        self.noperms_user = create_test_user(
            email="st_noperms@example.com",
            dni="DNI-ST-NOPERMS",
            is_superuser=False,
        )

        # Withdrawal reason for tests
        self.withdrawal_reason_cambio = WithdrawalReason.objects.create(
            code="CAMBIO_DOMICILIO", name="Cambio de domicilio"
        )

    def test_list_students_with_proper_permission(self):
        """Usuario autorizado puede listar estudiantes."""
        self.client.force_authenticate(user=self.limited_user)
        response = self.client.get("/api/students/student/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # DRF ViewSet list no está envuelto por BaseViewSet sino normal
        # Pero tiene la paginación global activada, por lo que StandardResultsSetPagination envuelve la respuesta
        self.assertTrue(response.json()["ok"])
        results = response.json()["data"]["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["student_code"], self.student.student_code)

    def test_list_students_without_permission_forbidden(self):
        """Usuario no autorizado recibe 403 al listar estudiantes."""
        self.client.force_authenticate(user=self.noperms_user)
        response = self.client.get("/api/students/student/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_enrollments_api_and_actions(self):
        """Prueba integraciones en EnrollmentViewSet (crear, retirar, transferir)."""
        admin = create_test_user(email="admin_st_test@example.com", is_superuser=True)
        self.client.force_authenticate(user=admin)

        # 1. Crear Matrícula
        data = {
            "student": self.student.id,
            "section": self.section.id,
        }
        response = self.client.post("/api/students/enrollments/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        enrollment_id = response.json()["data"]["id"]

        # 2. Consultar por sección
        response_sec = self.client.get(f"/api/students/enrollments/by-section/?section_id={self.section.id}")
        self.assertEqual(response_sec.status_code, status.HTTP_200_OK)

        # 3. Retirar Estudiante (con motivo)
        withdraw_data = {
            "reason": self.withdrawal_reason_cambio.id,
        }
        response_withdraw = self.client.post(f"/api/students/enrollments/{enrollment_id}/withdraw/", withdraw_data, format="json")
        self.assertEqual(response_withdraw.status_code, status.HTTP_200_OK)
        
        # Verificar que se persistieron el motivo y la fecha
        enrollment = Enrollment.objects.get(id=enrollment_id)
        self.assertEqual(enrollment.enrollment_status.code, "RET")
        self.assertEqual(enrollment.withdrawal_reason, self.withdrawal_reason_cambio)
        self.assertIsNotNone(enrollment.withdrawal_date)

        # 4. Transferir Estudiante a nueva sección
        new_section = Section.objects.create(
            school_year=self.school_year,
            academic_grade=self.grade,
            parallel="B",
            capacity=40,
        )
        transfer_data = {
            "section_id": new_section.id,
        }
        response_transfer = self.client.post(f"/api/students/enrollments/{enrollment_id}/transfer/", transfer_data, format="json")
        self.assertEqual(response_transfer.status_code, status.HTTP_200_OK)
        
        # Verificar estado ACT tras transferencia
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.section, new_section)
        self.assertEqual(enrollment.enrollment_status.code, "ACT")

    def test_student_representatives_api(self):
        """Prueba integraciones en StudentRepresentativeViewSet (crear, set_primary, unlink)."""
        admin = create_test_user(email="admin_st_rep@example.com", is_superuser=True)
        self.client.force_authenticate(user=admin)

        # Crear representante persona
        from apps.people.models import DocumentType
        doc_type, _ = DocumentType.objects.get_or_create(code="CC", defaults={"name": "Cedula"})
        representante = Person.objects.create(
            document_type=doc_type,
            document_number="88888888",
            names="Carlos",
            last_names="Perez",
            email="carlos@example.com",
        )

        # 1. Asignar Representante
        data = {
            "student": self.student.id,
            "person": representante.id,
            "kinship": "Padre",
            "is_primary": True,
        }
        response = self.client.post("/api/students/student-representative/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        rel_id = response.json()["data"]["id"]

        # 2. Cambiar Principal
        other_rep = Person.objects.create(
            document_type=doc_type,
            document_number="77777777",
            names="Marta",
            last_names="Perez",
            email="marta@example.com",
        )
        # Crear segunda relacion
        self.client.post("/api/students/student-representative/", {
            "student": self.student.id,
            "person": other_rep.id,
            "kinship": "Madre",
            "is_primary": False,
        }, format="json")

        set_primary_data = {
            "student": self.student.id,
            "person": other_rep.id,
        }
        response_primary = self.client.post("/api/students/student-representative/set_primary/", set_primary_data, format="json")
        self.assertEqual(response_primary.status_code, status.HTTP_200_OK)
        
        # Verificar cambio en BD
        rel1 = StudentRepresentative.objects.get(student=self.student, person=representante)
        rel2 = StudentRepresentative.objects.get(student=self.student, person=other_rep)
        self.assertFalse(rel1.is_primary)
        self.assertTrue(rel2.is_primary)

        # 3. Desasignar Representante (unlink)
        response_unlink = self.client.delete(f"/api/students/student-representative/{rel_id}/unlink/")
        self.assertEqual(response_unlink.status_code, status.HTTP_200_OK)
        self.assertFalse(StudentRepresentative.objects.filter(id=rel_id).exists())
