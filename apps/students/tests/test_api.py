from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date
from apps.institutions.models import Institution, School_Year
from apps.academic.models import Timing_Regime, Section
from apps.accounts.models import Role, User
from apps.students.models import Student, Representative


class StudentAPITest(APITestCase):
    """Tests para endpoints API de Student"""

    def setUp(self):
        """Crear datos de prueba"""
        self.institution = Institution.objects.create(
            name="Escuela API Test", code="EAT-001", address="Calle API", city="Quito"
        )
        self.school_year = School_Year.objects.create(
            institution=self.institution,
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )
        self.timing_regime = Timing_Regime.objects.create(
            school_year=self.school_year, name="Matutina"
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            timing_regime=self.timing_regime,
            level="Primaria",
            grade="6to",
            parallel="A",
            capacity=40,
        )
        self.student = Student.objects.create(
            dni="1234567890",
            names="Juan",
            last_names="Pérez García",
            birth_date=date(2012, 5, 15),
            section=self.section,
        )

        self.student_url = "/api/students/student/"

        # Crear usuario autenticado
        role = Role.objects.create(name="Admin")
        self.user = User.objects.create_user(
            email="student@test.com",
            dni="1717171717",
            names="Student",
            last_names="Tester",
            password="test_password_123",
            role=role,
            institution=self.institution,
        )
        self.client.force_authenticate(user=self.user)

    def test_list_students(self):
        """Probar listado de estudiantes"""
        response = self.client.get(self.student_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_student(self):
        """Probar creación de estudiante"""
        data = {
            "dni": "0987654321",
            "names": "María",
            "last_names": "García López",
            "birth_date": "2012-06-20",
            "section": self.section.id,
            "enrollment_number": "MAT-2024-002",
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
        student = Student.objects.create(
            dni="1111111111",
            names="Para Eliminar",
            last_names="Test",
            birth_date=date(2012, 5, 15),
            section=self.section,
        )
        response = self.client.delete(f"{self.student_url}{student.id}/")
        self.assertIn(
            response.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]
        )


class RepresentativeAPITest(APITestCase):
    """Tests para endpoints API de Representative"""

    def setUp(self):
        """Crear datos de prueba"""
        self.representative = Representative.objects.create(
            dni="9876543210",
            names="María",
            last_names="Pérez García",
            phone="0987654321",
        )

        self.representative_url = "/api/students/representative/"

        # Crear usuario autenticado
        institution = Institution.objects.create(
            name="Test Institution",
            code="TI-001",
            address="Test Address",
            city="Quito",
        )
        role = Role.objects.create(name="Admin")
        self.user = User.objects.create_user(
            email="representative@test.com",
            dni="1717171718",
            names="Representative",
            last_names="Tester",
            password="test_password_123",
            role=role,
            institution=institution,
        )
        self.client.force_authenticate(user=self.user)

    def test_list_representatives(self):
        """Probar listado de representantes"""
        response = self.client.get(self.representative_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_representative(self):
        """Probar creación de representante"""
        data = {
            "dni": "1111111111",
            "names": "Pedro",
            "last_names": "García López",
            "phone": "0987654322",
            "email": "pedro@example.com",
        }
        response = self.client.post(self.representative_url, data)
        self.assertIn(
            response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK]
        )

    def test_retrieve_representative(self):
        """Probar obtención de representante"""
        response = self.client.get(
            f"{self.representative_url}{self.representative.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_representative(self):
        """Probar actualización de representante"""
        data = {"phone": "0999999999"}
        response = self.client.patch(
            f"{self.representative_url}{self.representative.id}/", data
        )
        self.assertIn(
            response.status_code, [status.HTTP_200_OK, status.HTTP_202_ACCEPTED]
        )
