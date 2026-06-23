from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.iam.models import Permission, Role, RolePermission, UserRole
from apps.core.constants.permissions import institutions as perms
from apps.core.tests.helpers import create_test_user


class InstitutionsPermissionsTest(TestCase):
    """Verifica RBAC para cada ViewSet de institutions."""

    def setUp(self):
        self.client = APIClient()

        self.user_no_perm = create_test_user(
            email="no_perm_inst@test.com", dni="1000000001",
            names="No", last_names="Perm",
        )
        self.user_with_perm = create_test_user(
            email="with_perm_inst@test.com", dni="1000000002",
            names="With", last_names="Perm",
        )
        self.superuser = create_test_user(
            email="admin_inst@test.com", dni="1000000000",
            names="Admin", last_names="Inst", is_superuser=True,
        )

        perm_list = [
            perms.VIEW_SCHOOL_YEAR, perms.CREATE_SCHOOL_YEAR,
            perms.UPDATE_SCHOOL_YEAR, perms.DELETE_SCHOOL_YEAR,
            perms.VIEW_ACADEMIC_LEVEL, perms.CREATE_ACADEMIC_LEVEL,
            perms.UPDATE_ACADEMIC_LEVEL, perms.DELETE_ACADEMIC_LEVEL,
            perms.VIEW_ACADEMIC_SUBLEVEL, perms.CREATE_ACADEMIC_SUBLEVEL,
            perms.UPDATE_ACADEMIC_SUBLEVEL, perms.DELETE_ACADEMIC_SUBLEVEL,
            perms.VIEW_ACADEMIC_GRADE, perms.CREATE_ACADEMIC_GRADE,
            perms.UPDATE_ACADEMIC_GRADE, perms.DELETE_ACADEMIC_GRADE,
            perms.VIEW_SECTION, perms.CREATE_SECTION,
            perms.UPDATE_SECTION, perms.DELETE_SECTION,
        ]
        role = Role.objects.create(name="Institutions Test Role")
        for code in perm_list:
            p, _ = Permission.objects.get_or_create(code=code, defaults={"module": "institutions"})
            RolePermission.objects.create(role=role, permission=p)
        UserRole.objects.create(user=self.user_with_perm, role=role)

    def _test_endpoint(self, url, method="get", data=None):
        # 401
        resp = getattr(self.client, method)(url, data or {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED, f"Expected 401 for {method} {url}")
        # 403
        self.client.force_authenticate(user=self.user_no_perm)
        resp = getattr(self.client, method)(url, data or {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN, f"Expected 403 for {method} {url}")
        self.client.force_authenticate(user=None)

    # --- SchoolYearViewSet ---
    def test_school_year_list(self):
        self._test_endpoint("/api/institutions/school-year/")
    def test_school_year_create(self):
        self._test_endpoint("/api/institutions/school-year/", "post", {"name": "2025", "start_date": "2025-01-01", "end_date": "2025-12-31"})
    def test_school_year_detail(self):
        self._test_endpoint("/api/institutions/school-year/999/")

    def test_school_year_list_auth(self):
        self.client.force_authenticate(user=self.user_with_perm)
        resp = self.client.get("/api/institutions/school-year/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_school_year_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        resp = self.client.get("/api/institutions/school-year/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # --- AcademicLevelViewSet ---
    def test_academic_level_list(self):
        self._test_endpoint("/api/institutions/academic-levels/")
    def test_academic_level_create(self):
        self._test_endpoint("/api/institutions/academic-levels/", "post", {"name": "Primaria"})
    def test_academic_level_detail(self):
        self._test_endpoint("/api/institutions/academic-levels/999/")
    def test_academic_level_update(self):
        self._test_endpoint("/api/institutions/academic-levels/999/", "patch", {"name": "Modificado"})
    def test_academic_level_delete(self):
        self._test_endpoint("/api/institutions/academic-levels/999/", "delete")
    def test_academic_level_list_auth(self):
        self.client.force_authenticate(user=self.user_with_perm)
        resp = self.client.get("/api/institutions/academic-levels/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
    def test_academic_level_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        resp = self.client.get("/api/institutions/academic-levels/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # --- AcademicGradeViewSet ---
    def test_academic_grade_list(self):
        self._test_endpoint("/api/institutions/academic-grades/")
    def test_academic_grade_create(self):
        self._test_endpoint("/api/institutions/academic-grades/", "post", {"name": "7", "code": "7"})
    def test_academic_grade_detail(self):
        self._test_endpoint("/api/institutions/academic-grades/999/")
    def test_academic_grade_update(self):
        self._test_endpoint("/api/institutions/academic-grades/999/", "patch", {"name": "Modificado"})
    def test_academic_grade_delete(self):
        self._test_endpoint("/api/institutions/academic-grades/999/", "delete")
    def test_academic_grade_list_auth(self):
        self.client.force_authenticate(user=self.user_with_perm)
        resp = self.client.get("/api/institutions/academic-grades/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
    def test_academic_grade_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        resp = self.client.get("/api/institutions/academic-grades/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # --- AcademicSublevelViewSet ---
    def test_academic_sublevel_list(self):
        self._test_endpoint("/api/institutions/academic-sublevel/")
    def test_academic_sublevel_create(self):
        self._test_endpoint("/api/institutions/academic-sublevel/", "post", {"code": "PRE", "name": "Preparatoria", "academic_level": 999})
    def test_academic_sublevel_detail(self):
        self._test_endpoint("/api/institutions/academic-sublevel/999/")
    def test_academic_sublevel_list_auth(self):
        self.client.force_authenticate(user=self.user_with_perm)
        resp = self.client.get("/api/institutions/academic-sublevel/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
    def test_academic_sublevel_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        resp = self.client.get("/api/institutions/academic-sublevel/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # --- SectionViewSet ---
    def test_section_list(self):
        self._test_endpoint("/api/institutions/section/")
    def test_section_create(self):
        self._test_endpoint("/api/institutions/section/", "post", {"parallel": "A", "capacity": 30, "school_year": 999})
    def test_section_detail(self):
        self._test_endpoint("/api/institutions/section/999/")
    def test_section_update(self):
        self._test_endpoint("/api/institutions/section/999/", "patch", {"parallel": "B"})
    def test_section_delete(self):
        self._test_endpoint("/api/institutions/section/999/", "delete")
    def test_section_soft_delete(self):
        self._test_endpoint("/api/institutions/section/999/soft-delete/", "post")
    def test_section_list_auth(self):
        self.client.force_authenticate(user=self.user_with_perm)
        resp = self.client.get("/api/institutions/section/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
    def test_section_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        resp = self.client.get("/api/institutions/section/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
