from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.iam.models import Permission, Role, RolePermission, UserRole
from apps.core.constants.permissions import students as perms
from apps.core.tests.helpers import create_test_user


class StudentsPermissionsTest(TestCase):
    """Verifica RBAC para cada ViewSet de students."""

    def setUp(self):
        self.client = APIClient()

        self.user_no_perm = create_test_user(
            email="no_perm_stu@test.com", dni="3000000001",
            names="No", last_names="Perm",
        )
        self.user_with_perm = create_test_user(
            email="with_perm_stu@test.com", dni="3000000002",
            names="With", last_names="Perm",
        )
        self.superuser = create_test_user(
            email="admin_stu@test.com", dni="3000000000",
            names="Admin", last_names="Stu", is_superuser=True,
        )

        perm_codes = [
            perms.VIEW_STUDENT, perms.CREATE_STUDENT, perms.UPDATE_STUDENT, perms.DELETE_STUDENT,
            perms.VIEW_REPRESENTATIVE_RELATIONSHIP, perms.CREATE_REPRESENTATIVE_RELATIONSHIP, perms.UPDATE_REPRESENTATIVE_RELATIONSHIP, perms.DELETE_REPRESENTATIVE_RELATIONSHIP,
            perms.VIEW_ENROLLMENT, perms.CREATE_ENROLLMENT, perms.UPDATE_ENROLLMENT, perms.DELETE_ENROLLMENT,
            perms.WITHDRAW_STUDENT, perms.TRANSFER_STUDENT,
        ]
        role = Role.objects.create(name="Students Test Role")
        for code in perm_codes:
            p, _ = Permission.objects.get_or_create(code=code, defaults={"module": "students"})
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
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def _test_superuser(self, url, method="get", data=None):
        self.client.force_authenticate(user=self.superuser)
        resp = getattr(self.client, method)(url, data or {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # --- StudentViewSet ---
    def test_student_list(self):    self._test_401_403("/api/students/student/")
    def test_student_create(self):  self._test_401_403("/api/students/student/", "post", {"student_code": "EST-999"})
    def test_student_detail(self):  self._test_401_403("/api/students/student/999/")
    def test_student_list_auth(self):    self._test_auth("/api/students/student/")
    def test_student_superuser(self):    self._test_superuser("/api/students/student/")

    # --- StudentRepresentativeViewSet ---
    def test_rep_list(self):    self._test_401_403("/api/students/student-representative/")
    def test_rep_detail(self):  self._test_401_403("/api/students/student-representative/999/")
    def test_rep_list_auth(self):    self._test_auth("/api/students/student-representative/")
    def test_rep_superuser(self):    self._test_superuser("/api/students/student-representative/")

    # --- EnrollmentViewSet ---
    def test_enrollment_list(self):    self._test_401_403("/api/students/enrollments/")
    def test_enrollment_create(self):  self._test_401_403("/api/students/enrollments/", "post", {"enrollment_date": "2025-01-01"})
    def test_enrollment_detail(self):  self._test_401_403("/api/students/enrollments/999/")
    def test_enrollment_list_auth(self):    self._test_auth("/api/students/enrollments/")
    def test_enrollment_superuser(self):    self._test_superuser("/api/students/enrollments/")
