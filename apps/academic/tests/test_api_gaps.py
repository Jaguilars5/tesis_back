"""
Tests de integración y unitarios adicionales para el módulo academic.

Cubre brechas detectadas:
1. Pruebas de Modelos adicionales (Academic_Period, SubjectOffering, SubjectAcademicConfig, Teacher_Subject_Section, InterdisciplinaryProject, SubjectProject).
2. Pruebas sobre la capa de Servicios (AcademicService: create_academic_period, assign_teacher, list_teacher_assignments).
3. Pruebas de integración de APIs en ViewSets anteriormente no probados.
4. Pruebas de seguridad RBAC positivas y negativas.
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date

from apps.institutions.models import School_Year, AcademicLevel, AcademicGrade, Section
from apps.accounts.models import Role, User, Permission, UserRole, RolePermission
from apps.core.tests.helpers import create_test_user
from apps.core.constants.permissions import academic

from apps.academic.models import (
    Subject,
    Academic_Period,
    Teacher_Subject_Section,
    SubjectAcademicConfig,
    SubjectOffering,
    InterdisciplinaryProject,
    SubjectProject,
)
from apps.academic.services.academic_service import AcademicService


class AcademicModelGapsTest(TestCase):
    """Tests unitarios para los modelos de datos de academic no probados."""

    def setUp(self):
        self.school_year = School_Year.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )
        self.level = AcademicLevel.objects.create(name="Secundaria")
        self.grade = AcademicGrade.objects.create(
            academic_level=self.level, name="1ero Bachillerato", sequence_order=10
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            academic_grade=self.grade,
            parallel="A",
            capacity=30,
        )
        self.subject = Subject.objects.create(name="Matemáticas", code="MAT101")
        self.config = SubjectAcademicConfig.objects.create(
            subject=self.subject,
            academic_grade=self.grade,
            weekly_hours=5,
            pedagogical_order=1,
            is_required=True,
        )
        self.offering = SubjectOffering.objects.create(
            school_year=self.school_year,
            section=self.section,
            subject_academic_config=self.config,
        )
        self.period = Academic_Period.objects.create(
            school_year=self.school_year,
            name="Primer Trimestre",
            period_type="REGULAR",
            start_date=date(2024, 9, 15),
            end_date=date(2024, 12, 15),
            is_regular_period=True,
        )

    def test_academic_period_creation(self):
        """Verifica la creación del período académico."""
        self.assertEqual(self.period.name, "Primer Trimestre")
        self.assertEqual(self.period.period_type, "REGULAR")
        self.assertTrue(self.period.is_regular_period)
        self.assertEqual(str(self.period), "Primer Trimestre")

    def test_subject_academic_config_creation(self):
        """Verifica la relación de configuración de materia por grado."""
        self.assertEqual(self.config.weekly_hours, 5)
        self.assertEqual(self.config.pedagogical_order, 1)
        self.assertTrue(self.config.is_required)
        self.assertEqual(str(self.config), "Matemáticas - 1ero Bachillerato")

    def test_subject_offering_creation(self):
        """Verifica el modelo de oferta de materia."""
        self.assertEqual(self.offering.section, self.section)
        self.assertTrue(self.offering.active)

    def test_teacher_assignment_creation(self):
        """Verifica la asignación docente."""
        docente = create_test_user(email="docente_ac@example.com")
        assignment = Teacher_Subject_Section.objects.create(
            user=docente,
            subject_offering=self.offering,
        )
        self.assertEqual(assignment.user, docente)
        self.assertEqual(assignment.subject_offering, self.offering)
        self.assertTrue(assignment.active)

    def test_interdisciplinary_project_creation(self):
        """Verifica la creación del proyecto interdisciplinario."""
        project = InterdisciplinaryProject.objects.create(
            academic_period=self.period,
            title="Proyecto del Medio Ambiente",
            description="Cuidado del entorno escolar",
            start_date=date(2024, 10, 1),
            delivery_date=date(2024, 10, 31),
        )
        self.assertEqual(project.title, "Proyecto del Medio Ambiente")
        self.assertEqual(str(project), "Proyecto del Medio Ambiente")

    def test_subject_project_creation(self):
        """Verifica el modelo de asignatura del proyecto."""
        project = InterdisciplinaryProject.objects.create(
            academic_period=self.period,
            title="Proyecto del Medio Ambiente",
            start_date=date(2024, 10, 1),
            delivery_date=date(2024, 10, 31),
        )
        sub_proj = SubjectProject.objects.create(
            interdisciplinary_project=project,
            subject_offering=self.offering,
        )
        self.assertEqual(sub_proj.interdisciplinary_project, project)
        self.assertEqual(sub_proj.subject_offering, self.offering)


class AcademicServiceGapsTest(TestCase):
    """Tests para los métodos corregidos del AcademicService."""

    def setUp(self):
        self.school_year = School_Year.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )
        self.level = AcademicLevel.objects.create(name="Secundaria")
        self.grade = AcademicGrade.objects.create(
            academic_level=self.level, name="1ero Bachillerato", sequence_order=10
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            academic_grade=self.grade,
            parallel="A",
            capacity=30,
        )
        self.subject = Subject.objects.create(name="Matemáticas", code="MAT101")
        self.config = SubjectAcademicConfig.objects.create(
            subject=self.subject,
            academic_grade=self.grade,
            weekly_hours=5,
            pedagogical_order=1,
        )
        self.offering = SubjectOffering.objects.create(
            school_year=self.school_year,
            section=self.section,
            subject_academic_config=self.config,
        )

    def test_service_create_academic_period(self):
        """Prueba create_academic_period con parámetros reales."""
        period = AcademicService.create_academic_period(
            name="Segundo Trimestre",
            school_year_id=self.school_year.id,
            period_type="REGULAR",
            start_date=date(2024, 12, 1),
            end_date=date(2025, 3, 1),
        )
        self.assertIsNotNone(period.id)
        self.assertEqual(period.name, "Segundo Trimestre")

    def test_service_assign_teacher_success_and_duplicate(self):
        """Prueba assign_teacher y validación de duplicados."""
        docente = create_test_user(email="teacher_serv@example.com")
        assignment = AcademicService.assign_teacher(
            user_id=docente.id,
            subject_offering_id=self.offering.id,
        )
        self.assertEqual(assignment.user_id, docente.id)

        # Duplicado debe lanzar ValueError
        with self.assertRaises(ValueError):
            AcademicService.assign_teacher(
                user_id=docente.id,
                subject_offering_id=self.offering.id,
            )

    def test_service_list_teacher_assignments(self):
        """Prueba list_teacher_assignments filtrando correctamente."""
        docente = create_test_user(email="teacher_serv_list@example.com")
        assignment = AcademicService.assign_teacher(
            user_id=docente.id,
            subject_offering_id=self.offering.id,
        )
        
        results = AcademicService.list_teacher_assignments(user_id=docente.id)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().id, assignment.id)


class AcademicSecurityAndAPITest(TestCase):
    """Tests de integración de APIs y control de accesos RBAC."""

    def setUp(self):
        self.client = APIClient()

        self.school_year = School_Year.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )
        self.level = AcademicLevel.objects.create(name="Secundaria")
        self.grade = AcademicGrade.objects.create(
            academic_level=self.level, name="1ero Bachillerato", sequence_order=10
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            academic_grade=self.grade,
            parallel="A",
            capacity=30,
        )
        self.subject = Subject.objects.create(name="Matemáticas", code="MAT101")
        self.config = SubjectAcademicConfig.objects.create(
            subject=self.subject,
            academic_grade=self.grade,
            weekly_hours=5,
            pedagogical_order=1,
        )
        self.offering = SubjectOffering.objects.create(
            school_year=self.school_year,
            section=self.section,
            subject_academic_config=self.config,
        )
        self.period = Academic_Period.objects.create(
            school_year=self.school_year,
            name="Primer Trimestre",
            period_type="REGULAR",
            start_date=date(2024, 9, 15),
            end_date=date(2024, 12, 15),
        )

        # Crear permisos necesarios en BD
        self.view_period_perm = Permission.objects.create(
            code=academic.VIEW_PERIOD, module="academic", description="Ver períodos"
        )
        self.create_period_perm = Permission.objects.create(
            code=academic.CREATE_PERIOD, module="academic", description="Crear períodos"
        )

        # Rol limitado con permiso de lectura
        self.limited_role = Role.objects.create(name="Academic Limited", code="AC_LIM")
        RolePermission.objects.create(role=self.limited_role, permission=self.view_period_perm)

        # Usuario limitado (no superusuario)
        self.limited_user = create_test_user(
            email="academic_lim@example.com",
            dni="DNI-AC-LIM",
            is_superuser=False,
        )
        UserRole.objects.create(user=self.limited_user, role=self.limited_role)

        # Usuario sin permisos
        self.noperms_user = create_test_user(
            email="academic_noperms@example.com",
            dni="DNI-AC-NOPERMS",
            is_superuser=False,
        )

    def test_list_periods_with_proper_permission(self):
        """Usuario autorizado puede listar períodos académicos."""
        self.client.force_authenticate(user=self.limited_user)
        response = self.client.get("/api/academic/academic-period/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        
        # El BaseAcademicViewSet encapsula doblemente al paginar
        if "results" in response.data["data"]:
            results = response.data["data"]["results"]
        else:
            results = response.data["data"]["data"]["results"]
            
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Primer Trimestre")

    def test_list_periods_without_permission_forbidden(self):
        """Usuario no autorizado recibe 403 al listar períodos."""
        self.client.force_authenticate(user=self.noperms_user)
        response = self.client.get("/api/academic/academic-period/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_period_forbidden_then_allowed(self):
        """Usuario recibe 403 al intentar crear, y 201 al otorgarle el permiso de escritura."""
        self.client.force_authenticate(user=self.limited_user)
        data = {
            "school_year": self.school_year.id,
            "name": "Segundo Trimestre",
            "period_type": "REGULAR",
            "start_date": "2024-12-01",
            "end_date": "2025-03-01",
        }
        
        # Debe fallar con 403
        response_fail = self.client.post("/api/academic/academic-period/", data, format="json")
        self.assertEqual(response_fail.status_code, status.HTTP_403_FORBIDDEN)

        # Otorgar permiso de escritura al rol
        RolePermission.objects.create(role=self.limited_role, permission=self.create_period_perm)

        # Ahora debe tener éxito
        response_success = self.client.post("/api/academic/academic-period/", data, format="json")
        self.assertEqual(response_success.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_success.data["data"]["name"], "Segundo Trimestre")

    def test_teacher_subject_section_api(self):
        """Prueba integraciones en TeacherSubjectSectionViewSet."""
        # Se requiere superusuario para omitir otros permisos
        admin = create_test_user(email="admin_ac_test@example.com", is_superuser=True)
        self.client.force_authenticate(user=admin)

        docente = create_test_user(email="docente_api@example.com")
        data = {
            "user": docente.id,
            "subject_offering": self.offering.id,
            "active": True,
        }
        
        # POST
        response = self.client.post("/api/academic/teacher-subject-section/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        assign_id = response.data["data"]["id"]

        # GET detail
        response_get = self.client.get(f"/api/academic/teacher-subject-section/{assign_id}/")
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)
        
        # Soft delete action
        response_del = self.client.post(f"/api/academic/teacher-subject-section/{assign_id}/soft-delete/")
        self.assertEqual(response_del.status_code, status.HTTP_200_OK)
        self.assertFalse(response_del.data["data"]["active"])

    def test_interdisciplinary_project_api(self):
        """Prueba integraciones en InterdisciplinaryProjectViewSet y SubjectProjectViewSet."""
        admin = create_test_user(email="admin_ac_proj@example.com", is_superuser=True)
        self.client.force_authenticate(user=admin)

        # POST InterdisciplinaryProject
        proj_data = {
            "academic_period": self.period.id,
            "title": "Proyecto Tecnológico",
            "start_date": "2024-11-01",
            "delivery_date": "2024-11-30",
        }
        response_proj = self.client.post("/api/academic/interdisciplinary-projects/", proj_data, format="json")
        self.assertEqual(response_proj.status_code, status.HTTP_201_CREATED)
        proj_id = response_proj.data["data"]["id"]

        # POST SubjectProject
        sub_proj_data = {
            "interdisciplinary_project": proj_id,
            "subject_offering": self.offering.id,
        }
        response_sub = self.client.post("/api/academic/subject-projects/", sub_proj_data, format="json")
        self.assertEqual(response_sub.status_code, status.HTTP_201_CREATED)
