from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Permission, Role, RolePermission, User, UserPermission, UserRole
from apps.core.tests.helpers import create_test_user


class PermissionIntegrationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.role = Role.objects.create(name="Test Role")
        self.perm_grading = Permission.objects.create(
            codename="grading.view_note", module="grading"
        )
        self.perm_scheduling = Permission.objects.create(
            codename="scheduling.view_schedule", module="scheduling"
        )
        self.perm_analytics = Permission.objects.create(
            codename="analytics.view_risk_score", module="analytics"
        )
        self.perm_academic = Permission.objects.create(
            codename="academic.view_section", module="academic"
        )
        self.perm_students = Permission.objects.create(
            codename="students.view_student", module="students"
        )
        self.perm_institutions = Permission.objects.create(
            codename="institutions.view_institution", module="institutions"
        )
        self.perm_accounts = Permission.objects.create(
            codename="accounts.view_permission", module="accounts"
        )

        RolePermission.objects.create(
            role=self.role, permission=self.perm_grading
        )
        RolePermission.objects.create(
            role=self.role, permission=self.perm_scheduling
        )
        RolePermission.objects.create(
            role=self.role, permission=self.perm_analytics
        )
        RolePermission.objects.create(
            role=self.role, permission=self.perm_academic
        )
        RolePermission.objects.create(
            role=self.role, permission=self.perm_students
        )
        RolePermission.objects.create(
            role=self.role, permission=self.perm_institutions
        )
        RolePermission.objects.create(
            role=self.role, permission=self.perm_accounts
        )

        self.user_no_perms = create_test_user(
            email="noperms@test.com", dni="1234567890",
            names="Test", last_names="User",
        )

        self.user_with_perms = create_test_user(
            email="withperms@test.com", dni="1111111111",
            names="With", last_names="Perms",
        )

        self.inactive_user = create_test_user(
            email="inactive@test.com", dni="2222222222",
            names="Inactive", last_names="User",
            active=False,
        )

        self.superuser = create_test_user(
            email="admin@test.com", dni="0000000000",
            names="Admin", last_names="User",
            is_superuser=True,
        )
        UserRole.objects.create(user=self.user_with_perms, role=self.role)

    # ─── Sin autenticacion ────────────────────────────────────

    def test_grading_list_without_auth(self):
        response = self.client.get("/api/grading/student-notes/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_scheduling_list_without_auth(self):
        response = self.client.get("/api/scheduling/schedule-slots/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_analytics_list_without_auth(self):
        response = self.client.get("/api/analytics/student-risk-scores/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_academic_list_without_auth(self):
        response = self.client.get("/api/academic/section/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_students_list_without_auth(self):
        response = self.client.get("/api/students/student/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_institutions_list_without_auth(self):
        response = self.client.get("/api/institutions/institution/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_accounts_list_without_auth(self):
        response = self.client.get("/api/accounts/permissions/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ─── Sin permisos → 403 ───────────────────────────────────

    def test_grading_list_no_permission(self):
        self.client.force_authenticate(user=self.user_no_perms)
        response = self.client.get("/api/grading/student-notes/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_scheduling_list_no_permission(self):
        self.client.force_authenticate(user=self.user_no_perms)
        response = self.client.get("/api/scheduling/schedule-slots/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_analytics_list_no_permission(self):
        self.client.force_authenticate(user=self.user_no_perms)
        response = self.client.get("/api/analytics/student-risk-scores/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_academic_list_no_permission(self):
        self.client.force_authenticate(user=self.user_no_perms)
        response = self.client.get("/api/academic/section/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_students_list_no_permission(self):
        self.client.force_authenticate(user=self.user_no_perms)
        response = self.client.get("/api/students/student/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_institutions_list_no_permission(self):
        self.client.force_authenticate(user=self.user_no_perms)
        response = self.client.get("/api/institutions/institution/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_accounts_list_no_permission(self):
        self.client.force_authenticate(user=self.user_no_perms)
        response = self.client.get("/api/accounts/permissions/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ─── Con permisos → 200 ───────────────────────────────────

    def test_grading_list_with_permission(self):
        self.client.force_authenticate(user=self.user_with_perms)
        response = self.client.get("/api/grading/student-notes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_scheduling_list_with_permission(self):
        self.client.force_authenticate(user=self.user_with_perms)
        response = self.client.get("/api/scheduling/schedule-slots/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_analytics_list_with_permission(self):
        self.client.force_authenticate(user=self.user_with_perms)
        response = self.client.get("/api/analytics/student-risk-scores/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_academic_list_with_permission(self):
        self.client.force_authenticate(user=self.user_with_perms)
        response = self.client.get("/api/academic/section/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_students_list_with_permission(self):
        self.client.force_authenticate(user=self.user_with_perms)
        response = self.client.get("/api/students/student/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_institutions_list_with_permission(self):
        self.client.force_authenticate(user=self.user_with_perms)
        response = self.client.get("/api/institutions/institution/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_accounts_list_with_permission(self):
        self.client.force_authenticate(user=self.user_with_perms)
        response = self.client.get("/api/accounts/permissions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ─── Superusuario bypass → 200 ────────────────────────────

    def test_grading_list_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get("/api/grading/student-notes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_accounts_list_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get("/api/accounts/permissions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ─── Permiso revocado via UserPermission → 403 ────────────

    def test_permission_revoked_via_user_permission(self):
        UserPermission.objects.create(
            user=self.user_with_perms,
            permission=self.perm_grading,
            granted=False,
        )
        self.client.force_authenticate(user=self.user_with_perms)
        response = self.client.post("/api/grading/student-notes/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ─── Usuario inactivo → 401/403 ───────────────────────────

    def test_inactive_user_rejected(self):
        self.client.force_authenticate(user=self.inactive_user)
        response = self.client.get("/api/accounts/permissions/")
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    # ─── Endpoints publicos (login/refresh) ────────────────────

    def test_login_is_public(self):
        response = self.client.post("/api/accounts/login/", {
            "email": "withperms@test.com",
            "password": "test_password_123",
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_refresh_is_public(self):
        login_response = self.client.post("/api/accounts/login/", {
            "email": "withperms@test.com",
            "password": "test_password_123",
        })
        refresh_token = login_response.data.get(
            "refresh", login_response.data.get("data", {}).get("refresh")
        )
        if not refresh_token:
            self.fail("No refresh token in login response")
        response = self.client.post(
            "/api/accounts/refresh/", {"refresh": refresh_token}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
