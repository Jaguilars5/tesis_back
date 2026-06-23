from datetime import date

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.iam.models import Permission, Role, RolePermission, UserRole
from apps.core.constants.permissions import academic as perms
from apps.core.tests.helpers import create_test_user


class AcademicPermissionsTest(TestCase):
    """Verifica RBAC para cada ViewSet de academic."""

    def setUp(self):
        self.client = APIClient()

        self.user_no_perm = create_test_user(
            email="no_perm_acad@test.com", dni="2000000001",
            names="No", last_names="Perm",
        )
        self.user_with_perm = create_test_user(
            email="with_perm_acad@test.com", dni="2000000002",
            names="With", last_names="Perm",
        )
        self.superuser = create_test_user(
            email="admin_acad@test.com", dni="2000000000",
            names="Admin", last_names="Acad", is_superuser=True,
        )

        perm_codes = [
            perms.VIEW_SUBJECT, perms.CREATE_SUBJECT, perms.UPDATE_SUBJECT, perms.DELETE_SUBJECT,
            perms.VIEW_PERIOD, perms.CREATE_PERIOD, perms.UPDATE_PERIOD, perms.DELETE_PERIOD,
            perms.VIEW_PERIOD_TYPE, perms.CREATE_PERIOD_TYPE, perms.UPDATE_PERIOD_TYPE, perms.DELETE_PERIOD_TYPE,
            perms.VIEW_TEACHER_SUBJECT, perms.CREATE_TEACHER_SUBJECT, perms.UPDATE_TEACHER_SUBJECT, perms.DELETE_TEACHER_SUBJECT,
            perms.VIEW_SUBJECT_CONFIG, perms.CREATE_SUBJECT_CONFIG, perms.UPDATE_SUBJECT_CONFIG, perms.DELETE_SUBJECT_CONFIG,
            perms.VIEW_SUBJECT_OFFERING, perms.CREATE_SUBJECT_OFFERING, perms.UPDATE_SUBJECT_OFFERING, perms.DELETE_SUBJECT_OFFERING,

        ]
        role = Role.objects.create(name="Academic Test Role")
        for code in perm_codes:
            p, _ = Permission.objects.get_or_create(code=code, defaults={"module": "academic"})
            RolePermission.objects.create(role=role, permission=p)
        UserRole.objects.create(user=self.user_with_perm, role=role)

    def _test_401_403(self, url, method="get", data=None):
        resp = getattr(self.client, method)(url, data or {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED, f"Expected 401 for {method} {url}")
        self.client.force_authenticate(user=self.user_no_perm)
        resp = getattr(self.client, method)(url, data or {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN, f"Expected 403 for {method} {url}")
        self.client.force_authenticate(user=None)

    def _test_auth(self, url, method="get", data=None):
        self.client.force_authenticate(user=self.user_with_perm)
        resp = getattr(self.client, method)(url, data or {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK, f"Expected 200 for {method} {url}: {getattr(resp, 'data', '')}")

    def _test_superuser(self, url, method="get", data=None):
        self.client.force_authenticate(user=self.superuser)
        resp = getattr(self.client, method)(url, data or {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK, f"Expected 200 for superuser {method} {url}")

    # --- SubjectViewSet ---
    def test_subject_list(self):    self._test_401_403("/api/academic/subject/")
    def test_subject_create(self):  self._test_401_403("/api/academic/subject/", "post", {"name": "Math", "code": "MATH-01"})
    def test_subject_detail(self):  self._test_401_403("/api/academic/subject/999/")
    def test_subject_list_auth(self):    self._test_auth("/api/academic/subject/")
    def test_subject_superuser(self):    self._test_superuser("/api/academic/subject/")

    # --- AcademicPeriodViewSet ---
    def test_period_list(self):    self._test_401_403("/api/academic/academic-period/")
    def test_period_create(self):  self._test_401_403("/api/academic/academic-period/", "post", {"name": "P1", "start_date": "2025-01-01", "end_date": "2025-03-31"})
    def test_period_detail(self):  self._test_401_403("/api/academic/academic-period/999/")
    def test_period_list_auth(self):    self._test_auth("/api/academic/academic-period/")
    def test_period_superuser(self):    self._test_superuser("/api/academic/academic-period/")

    # --- TeacherSubjectSectionViewSet ---
    def test_tss_list(self):    self._test_401_403("/api/academic/teacher-subject-section/")
    def test_tss_detail(self):  self._test_401_403("/api/academic/teacher-subject-section/999/")
    def test_tss_list_auth(self):    self._test_auth("/api/academic/teacher-subject-section/")
    def test_tss_superuser(self):    self._test_superuser("/api/academic/teacher-subject-section/")

    # --- SubjectAcademicConfigViewSet ---
    def test_config_list(self):    self._test_401_403("/api/academic/subject-academic-configs/")
    def test_config_create(self):  self._test_401_403("/api/academic/subject-academic-configs/", "post", {"weekly_hours": 5})
    def test_config_detail(self):  self._test_401_403("/api/academic/subject-academic-configs/999/")
    def test_config_list_auth(self):    self._test_auth("/api/academic/subject-academic-configs/")
    def test_config_superuser(self):    self._test_superuser("/api/academic/subject-academic-configs/")

    # --- SubjectOfferingViewSet ---
    def test_offering_list(self):    self._test_401_403("/api/academic/subject-offerings/")
    def test_offering_detail(self):  self._test_401_403("/api/academic/subject-offerings/999/")
    def test_offering_list_auth(self):    self._test_auth("/api/academic/subject-offerings/")
    def test_offering_superuser(self):    self._test_superuser("/api/academic/subject-offerings/")

    # --- PeriodTypeViewSet ---
    def test_period_type_list(self):    self._test_401_403("/api/academic/period-types/")
    def test_period_type_create(self):  self._test_401_403("/api/academic/period-types/", "post", {"code": "EXTRA", "name": "Extra"})
    def test_period_type_detail(self):  self._test_401_403("/api/academic/period-types/999/")
    def test_period_type_list_auth(self):    self._test_auth("/api/academic/period-types/")
    def test_period_type_superuser(self):    self._test_superuser("/api/academic/period-types/")
