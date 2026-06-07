"""
Tests de integración y unitarios adicionales para el módulo institutions.

Cubre brechas detectadas:
1. Pruebas de Modelos adicionales (AcademicLevel, AcademicGrade).
2. Pruebas de integración de APIs en ViewSets anteriormente no probados (AcademicLevelViewSet, AcademicGradeViewSet).
3. Pruebas de seguridad RBAC positivas y negativas.
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date

from apps.accounts.models import Role, User, Permission, UserRole, RolePermission
from apps.core.tests.helpers import create_test_user
from apps.core.constants.permissions import institutions

from apps.institutions.models import School_Year, DocumentType, AcademicLevel, AcademicGrade


class InstitutionsModelGapsTest(TestCase):
    """Tests unitarios para los modelos de datos de institutions no probados."""

    def setUp(self):
        self.level = AcademicLevel.objects.create(name="Secundaria")
        self.grade = AcademicGrade.objects.create(
            academic_level=self.level,
            name="1ero Bachillerato",
            subnivel="BACHILLERATO",
            sequence_order=10,
        )

    def test_academic_level_creation(self):
        """Verifica la creación del nivel académico."""
        self.assertEqual(self.level.name, "Secundaria")
        self.assertTrue(self.level.active)
        self.assertEqual(str(self.level), "Secundaria")

    def test_academic_grade_creation(self):
        """Verifica la creación del grado académico."""
        self.assertEqual(self.grade.name, "1ero Bachillerato")
        self.assertEqual(self.grade.subnivel, "BACHILLERATO")
        self.assertEqual(self.grade.sequence_order, 10)
        self.assertTrue(self.grade.active)
        self.assertEqual(str(self.grade), "Secundaria - 1ero Bachillerato")


class InstitutionsSecurityAndAPITest(TestCase):
    """Tests de integración de APIs y control de accesos RBAC."""

    def setUp(self):
        self.client = APIClient()

        self.level = AcademicLevel.objects.create(name="Primaria")
        self.grade = AcademicGrade.objects.create(
            academic_level=self.level,
            name="5to EGB",
            sequence_order=5,
        )
        self.school_year = School_Year.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )

        # Crear permisos necesarios en BD
        self.view_level_perm = Permission.objects.create(
            code=institutions.VIEW_ACADEMIC_LEVEL, module="institutions", description="Ver nivel académico"
        )
        self.create_level_perm = Permission.objects.create(
            code=institutions.CREATE_ACADEMIC_LEVEL, module="institutions", description="Crear nivel académico"
        )
        self.view_sy_perm = Permission.objects.create(
            code=institutions.VIEW_SCHOOL_YEAR, module="institutions", description="Ver año escolar"
        )
        self.create_sy_perm = Permission.objects.create(
            code=institutions.CREATE_SCHOOL_YEAR, module="institutions", description="Crear año escolar"
        )

        # Rol limitado con permiso de lectura de nivel académico
        self.limited_role = Role.objects.create(name="Inst Limited", code="INS_LIM")
        RolePermission.objects.create(role=self.limited_role, permission=self.view_level_perm)

        # Usuario limitado (no superusuario)
        self.limited_user = create_test_user(
            email="inst_lim@example.com",
            dni="DNI-INS-LIM",
            is_superuser=False,
        )
        UserRole.objects.create(user=self.limited_user, role=self.limited_role)

        # Usuario sin permisos
        self.noperms_user = create_test_user(
            email="inst_noperms@example.com",
            dni="DNI-INS-NOPERMS",
            is_superuser=False,
        )

    def test_list_academic_levels_with_proper_permission(self):
        """Usuario autorizado puede listar niveles académicos."""
        self.client.force_authenticate(user=self.limited_user)
        response = self.client.get("/api/institutions/academic-levels/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # StandardResponseRenderer envuelve la respuesta de DRF de lista paginada
        self.assertTrue(response.data["ok"])
        results = response.data["data"]["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Primaria")

    def test_list_academic_levels_without_permission_forbidden(self):
        """Usuario no autorizado recibe 403 al listar niveles."""
        self.client.force_authenticate(user=self.noperms_user)
        response = self.client.get("/api/institutions/academic-levels/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_academic_level_forbidden_then_allowed(self):
        """Usuario recibe 403 al intentar crear, y 201 al otorgarle el permiso de escritura."""
        self.client.force_authenticate(user=self.limited_user)
        data = {"name": "Inicial"}
        
        # Debe fallar con 403
        response_fail = self.client.post("/api/institutions/academic-levels/", data, format="json")
        self.assertEqual(response_fail.status_code, status.HTTP_403_FORBIDDEN)

        # Otorgar permiso de escritura al rol
        RolePermission.objects.create(role=self.limited_role, permission=self.create_level_perm)

        # Ahora debe tener éxito
        response_success = self.client.post("/api/institutions/academic-levels/", data, format="json")
        self.assertEqual(response_success.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_success.data["name"], "Inicial")

    def test_academic_grades_api_and_rbac(self):
        """Prueba de integración de AcademicGradeViewSet con RBAC."""
        self.client.force_authenticate(user=self.limited_user)
        
        # GET List
        response_list = self.client.get("/api/institutions/academic-grades/")
        self.assertEqual(response_list.status_code, status.HTTP_200_OK)
        self.assertTrue(response_list.data["ok"])
        
        # POST sin permiso (403)
        grade_data = {
            "academic_level": self.level.id,
            "name": "6to EGB",
            "sequence_order": 6,
        }
        response_post_fail = self.client.post("/api/institutions/academic-grades/", grade_data, format="json")
        self.assertEqual(response_post_fail.status_code, status.HTTP_403_FORBIDDEN)

        # Otorgar permiso
        RolePermission.objects.create(role=self.limited_role, permission=self.create_level_perm)
        response_post_success = self.client.post("/api/institutions/academic-grades/", grade_data, format="json")
        self.assertEqual(response_post_success.status_code, status.HTTP_201_CREATED)

    def test_school_year_api_and_rbac(self):
        """Prueba de integración de SchoolYearViewSet con RBAC."""
        # limited_user solo tiene view_academic_level, no view_school_year
        self.client.force_authenticate(user=self.limited_user)
        response_fail = self.client.get("/api/institutions/school-year/")
        self.assertEqual(response_fail.status_code, status.HTTP_403_FORBIDDEN)

        # Otorgar permiso de lectura del año escolar
        RolePermission.objects.create(role=self.limited_role, permission=self.view_sy_perm)
        response_success = self.client.get("/api/institutions/school-year/")
        self.assertEqual(response_success.status_code, status.HTTP_200_OK)
        self.assertTrue(response_success.data["ok"])
