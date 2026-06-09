from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.iam.models import Permission, Role, RolePermission, UserRole
from apps.core.constants.permissions import attendance as perms
from apps.core.tests.helpers import create_test_user


class AttendancePermissionsTest(TestCase):
    """Verifica RBAC para cada ViewSet de attendance."""

    def setUp(self):
        self.client = APIClient()

        self.user_no_perm = create_test_user(
            email="no_perm_att@test.com", dni="5000000001",
            names="No", last_names="Perm",
        )
        self.user_with_perm = create_test_user(
            email="with_perm_att@test.com", dni="5000000002",
            names="With", last_names="Perm",
        )
        self.superuser = create_test_user(
            email="admin_att@test.com", dni="5000000000",
            names="Admin", last_names="Att", is_superuser=True,
        )

        perm_codes = [
            perms.VIEW_ATTENDANCE, perms.CREATE_ATTENDANCE, perms.UPDATE_ATTENDANCE, perms.DELETE_ATTENDANCE,
            perms.VIEW_ATTENDANCE_STATUS, perms.CREATE_ATTENDANCE_STATUS, perms.UPDATE_ATTENDANCE_STATUS, perms.DELETE_ATTENDANCE_STATUS,
            perms.VIEW_ABSENCE_TYPE, perms.CREATE_ABSENCE_TYPE, perms.UPDATE_ABSENCE_TYPE, perms.DELETE_ABSENCE_TYPE,
        ]
        role = Role.objects.create(name="Attendance Test Role")
        for code in perm_codes:
            p, _ = Permission.objects.get_or_create(code=code, defaults={"module": "attendance"})
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

    # --- AttendanceViewSet ---
    def test_att_list(self):    self._test_401_403("/api/attendance/attendances/")
    def test_att_create(self):  self._test_401_403("/api/attendance/attendances/", "post", {"attendance_date": "2025-01-01"})
    def test_att_detail(self):  self._test_401_403("/api/attendance/attendances/999/")
    def test_att_list_auth(self):    self._test_auth("/api/attendance/attendances/")
    def test_att_superuser(self):    self._test_superuser("/api/attendance/attendances/")

    # --- AttendanceStatusViewSet ---
    def test_att_status_list(self):    self._test_401_403("/api/attendance/attendance-statuses/")
    def test_att_status_create(self):  self._test_401_403("/api/attendance/attendance-statuses/", "post", {"code": "P", "name": "Presente"})
    def test_att_status_detail(self):  self._test_401_403("/api/attendance/attendance-statuses/999/")
    def test_att_status_list_auth(self):    self._test_auth("/api/attendance/attendance-statuses/")
    def test_att_status_superuser(self):    self._test_superuser("/api/attendance/attendance-statuses/")

    # --- AbsenceTypeViewSet ---
    def test_abs_type_list(self):    self._test_401_403("/api/attendance/absence-types/")
    def test_abs_type_create(self):  self._test_401_403("/api/attendance/absence-types/", "post", {"code": "J", "name": "Justificada"})
    def test_abs_type_detail(self):  self._test_401_403("/api/attendance/absence-types/999/")
    def test_abs_type_list_auth(self):    self._test_auth("/api/attendance/absence-types/")
    def test_abs_type_superuser(self):    self._test_superuser("/api/attendance/absence-types/")