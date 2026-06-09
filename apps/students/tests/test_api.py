from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date
from apps.institutions.models import AcademicGrade, AcademicLevel, AcademicSublevel, SchoolYear
from apps.institutions.models import Section
from apps.iam.models import Role, User
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.students.models import EnrollmentStatus, Student

# Compatibilidad Python 3.14: patch Context.__copy__
import django.template.context as _context


def _safe_base_copy(self):
    duplicate = object.__new__(type(self))
    duplicate.dicts = self.dicts[:]
    return duplicate


_context.BaseContext.__copy__ = _safe_base_copy


class StudentAPITest(APITestCase):
    """Tests para endpoints API de Student"""

    def setUp(self):
        """Crear datos de prueba"""
        self.school_year = SchoolYear.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )
        self.academic_level = AcademicLevel.objects.create(name="Primaria")
        self.academic_sublevel = AcademicSublevel.objects.create(
            academic_level=self.academic_level, code="BASICA", name="Básica"
        )
        self.academic_grade = AcademicGrade.objects.create(
            academic_sublevel=self.academic_sublevel, name="6to", sequence_order=6
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            academic_grade=self.academic_grade,
            parallel="A",
            capacity=40,
        )
        self.student = create_test_student(
            document_number="1234567890",
            names="Juan",
            last_names="Pérez García",
            birth_date=date(2012, 5, 15),
        )

        self.student_url = "/api/students/student/"

        # Crear usuario autenticado
        role = Role.objects.create(name="Admin")
        self.user = create_test_user(
            email="student@test.com",
            dni="1717171717",
            names="Student",
            last_names="Tester",
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_list_students(self):
        """Probar listado de estudiantes"""
        response = self.client.get(self.student_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_student(self):
        """Probar creación de estudiante"""
        data = {
            "document_number": "0987654321",
            "names": "María",
            "last_names": "García López",
            "birth_date": "2012-06-20",
        }
        response = self.client.post(self.student_url, data)
        self.assertIn(
            response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK]
        )

    def test_retrieve_student(self):
        """Probar obtención de estudiante"""
        response = self.client.get(f"{self.student_url}{self.student.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_student(self):
        """Probar actualización de estudiante"""
        data = {"names": "Juan Pablo"}
        response = self.client.patch(f"{self.student_url}{self.student.id}/", data)
        self.assertIn(
            response.status_code, [status.HTTP_200_OK, status.HTTP_202_ACCEPTED]
        )

    def test_delete_student(self):
        """Probar eliminación (soft delete) de estudiante"""
        student = create_test_student(
            document_number="1111111111",
            names="Para Eliminar",
            last_names="Test",
            birth_date=date(2012, 5, 15),
        )
        response = self.client.delete(f"{self.student_url}{student.id}/")
        self.assertIn(
            response.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]
        )


class EnrollmentStatusAPITest(APITestCase):
    def setUp(self):
        self.role = Role.objects.create(name="Admin")
        self.user = create_test_user(
            email="enrstatus@test.com",
            dni="4040404040",
            names="EnrStatus",
            last_names="Tester",
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        EnrollmentStatus.objects.get_or_create(code="ACT", defaults={"name": "Activa"})
        EnrollmentStatus.objects.create(code="RET", name="Retirado")
        self.url = "/api/students/enrollment-statuses/"

    def test_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve(self):
        obj = EnrollmentStatus.objects.first()
        response = self.client.get(f"{self.url}{obj.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_not_allowed(self):
        response = self.client.post(self.url, {"code": "GRAD", "name": "Graduado"})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
