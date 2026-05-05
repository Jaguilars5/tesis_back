from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date
from django.contrib.auth import get_user_model
from apps.institutions.models import Institution, School_Year
from apps.accounts.models import Role
from ..models import Section, Subject, Timing_Regime, Config_Academic

User = get_user_model()


class AcademicAPITest(APITestCase):
    """Tests para endpoints API de Academic"""

    def setUp(self):
        """Crear datos de prueba"""
        # Crear institución para el usuario
        self.user_institution = Institution.objects.create(
            name="Institución de Prueba", code="INST-TEST", city="Quito"
        )

        # Crear rol para el usuario
        self.role = Role.objects.create(name="Admin")

        # Crear usuario para autenticación
        self.user = User.objects.create(
            email="test@example.com",
            dni="1234567890",
            names="Test",
            last_names="User",
            role=self.role,
            institution=self.user_institution,
            is_superuser=True,
        )
        self.user.set_password("test_password_123")
        self.user.save()
        self.client.force_authenticate(user=self.user)

        # Crear datos académicos
        self.institution = Institution.objects.create(
            name="Colegio API Test", code="CAT-001", address="Calle API", city="Quito"
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
        self.subject = Subject.objects.create(
            school_year=self.school_year,
            section=self.section,
            name="Matemática",
            code="MAT-001",
            weekly_hours=5,
            approve_percentage=70,
        )

        self.section_url = "/api/academic/section/"
        self.subject_url = "/api/academic/subject/"
        self.timing_regime_url = "/api/academic/timing-regime/"

    def test_list_sections(self):
        """Probar listado de secciones"""
        response = self.client.get(self.section_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_section(self):
        """Probar creación de sección"""
        data = {
            "school_year": self.school_year.id,
            "timing_regime": self.timing_regime.id,
            "level": "Primaria",
            "grade": "5to",
            "parallel": "B",
            "capacity": 35,
        }
        response = self.client.post(self.section_url, data)
        self.assertIn(
            response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK]
        )

    def test_retrieve_section(self):
        """Probar obtención de sección"""
        response = self.client.get(f"{self.section_url}{self.section.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_section(self):
        """Probar actualización de sección"""
        data = {"capacity": 50}
        response = self.client.patch(f"{self.section_url}{self.section.id}/", data)
        self.assertIn(
            response.status_code, [status.HTTP_200_OK, status.HTTP_202_ACCEPTED]
        )

    def test_list_subjects(self):
        """Probar listado de asignaturas"""
        response = self.client.get(self.subject_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_subject(self):
        """Probar creación de asignatura"""
        data = {
            "school_year": self.school_year.id,
            "section": self.section.id,
            "name": "Lenguaje",
            "code": "LEN-001",
            "weekly_hours": 3,
            "approve_percentage": 75,
        }
        response = self.client.post(self.subject_url, data)
        self.assertIn(
            response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK]
        )

    def test_retrieve_subject(self):
        """Probar obtención de asignatura"""
        response = self.client.get(f"{self.subject_url}{self.subject.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_subject(self):
        """Probar actualización de asignatura"""
        data = {"weekly_hours": 4}
        response = self.client.patch(f"{self.subject_url}{self.subject.id}/", data)
        self.assertIn(
            response.status_code, [status.HTTP_200_OK, status.HTTP_202_ACCEPTED]
        )

    def test_list_timing_regimes(self):
        """Probar listado de regímenes horarios"""
        response = self.client.get(self.timing_regime_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_timing_regime(self):
        """Probar creación de régimen horario"""
        data = {
            "school_year": self.school_year.id,
            "name": "Vespertina",
            "description": "Jornada de tarde",
        }
        response = self.client.post(self.timing_regime_url, data)
        self.assertIn(
            response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK]
        )

    def test_retrieve_timing_regime(self):
        """Probar obtención de régimen horario"""
        response = self.client.get(f"{self.timing_regime_url}{self.timing_regime.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
