from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Permission, Role, RolePermission, User, UserRole
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
            names="With", last_names="Perm", user_type="ADMIN",
        )
        self.superuser = create_test_user(
            email="admin_inst@test.com", dni="1000000000",
            names="Admin", last_names="Inst", is_superuser=True,
        )

        perm_list = [
            perms.VIEW_SCHOOL_YEAR, perms.CREATE_SCHOOL_YEAR,
            perms.UPDATE_SCHOOL_YEAR, perms.DELETE_SCHOOL_YEAR,
            perms.VIEW_DOCUMENT_TYPE,
            perms.VIEW_ACADEMIC_LEVEL, perms.CREATE_ACADEMIC_LEVEL,
            perms.UPDATE_ACADEMIC_LEVEL, perms.DELETE_ACADEMIC_LEVEL,
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

    # --- DocumentTypeViewSet ---
    def test_document_type_list(self):
        self._test_endpoint("/api/institutions/document-types/")
    def test_document_type_detail(self):
        self._test_endpoint("/api/institutions/document-types/999/")
    def test_document_type_list_auth(self):
        self.client.force_authenticate(user=self.user_with_perm)
        resp = self.client.get("/api/institutions/document-types/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
    def test_document_type_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        resp = self.client.get("/api/institutions/document-types/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # --- AcademicLevelViewSet ---
    def test_academic_level_list(self):
        self._test_endpoint("/api/institutions/academic-levels/")
    def test_academic_level_create(self):
        self._test_endpoint("/api/institutions/academic-levels/", "post", {"name": "Primaria"})
    def test_academic_level_detail(self):
        self._test_endpoint("/api/institutions/academic-levels/999/")
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
        self._test_endpoint("/api/institutions/academic-grades/", "post", {"name": "7", "sequence_order": 1})
    def test_academic_grade_list_auth(self):
        self.client.force_authenticate(user=self.user_with_perm)
        resp = self.client.get("/api/institutions/academic-grades/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
    def test_academic_grade_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        resp = self.client.get("/api/institutions/academic-grades/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
