from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Permission, Role, RolePermission, UserRole
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
            names="With", last_names="Perm", user_type="ADMIN",
        )
        self.superuser = create_test_user(
            email="admin_att@test.com", dni="5000000000",
            names="Admin", last_names="Att", is_superuser=True,
        )

        perm_codes = [
            perms.VIEW_ATTENDANCE, perms.CREATE_ATTENDANCE, perms.UPDATE_ATTENDANCE, perms.DELETE_ATTENDANCE,
            perms.VIEW_CONDUCT_INCIDENT, perms.CREATE_CONDUCT_INCIDENT, perms.UPDATE_CONDUCT_INCIDENT, perms.DELETE_CONDUCT_INCIDENT,
            perms.VIEW_BEHAVIOR_EVALUATION, perms.CREATE_BEHAVIOR_EVALUATION, perms.UPDATE_BEHAVIOR_EVALUATION, perms.DELETE_BEHAVIOR_EVALUATION,
            perms.VIEW_INCIDENT_TYPE, perms.CREATE_INCIDENT_TYPE, perms.UPDATE_INCIDENT_TYPE, perms.DELETE_INCIDENT_TYPE,
            perms.VIEW_SOCIOEMOTIONAL_SKILL, perms.CREATE_SOCIOEMOTIONAL_SKILL, perms.UPDATE_SOCIOEMOTIONAL_SKILL, perms.DELETE_SOCIOEMOTIONAL_SKILL,
            perms.VIEW_SKILL_EVALUATION, perms.CREATE_SKILL_EVALUATION, perms.UPDATE_SKILL_EVALUATION, perms.DELETE_SKILL_EVALUATION,
            perms.VIEW_ATTENDANCE_STATUS, perms.CREATE_ATTENDANCE_STATUS, perms.UPDATE_ATTENDANCE_STATUS, perms.DELETE_ATTENDANCE_STATUS,
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

    # --- ConductIncidentViewSet ---
    def test_ci_list(self):    self._test_401_403("/api/attendance/conduct-incidents/")
    def test_ci_create(self):  self._test_401_403("/api/attendance/conduct-incidents/", "post", {"incident_date": "2025-01-01", "severity": 1})
    def test_ci_detail(self):  self._test_401_403("/api/attendance/conduct-incidents/999/")
    def test_ci_list_auth(self):    self._test_auth("/api/attendance/conduct-incidents/")
    def test_ci_superuser(self):    self._test_superuser("/api/attendance/conduct-incidents/")

    # --- BehaviorEvaluationViewSet ---
    def test_be_list(self):    self._test_401_403("/api/attendance/behavior-evaluations/")
    def test_be_detail(self):  self._test_401_403("/api/attendance/behavior-evaluations/999/")
    def test_be_list_auth(self):    self._test_auth("/api/attendance/behavior-evaluations/")
    def test_be_superuser(self):    self._test_superuser("/api/attendance/behavior-evaluations/")

    # --- IncidentTypeViewSet ---
    def test_it_list(self):    self._test_401_403("/api/attendance/incident-types/")
    def test_it_create(self):  self._test_401_403("/api/attendance/incident-types/", "post", {"code": "TEST", "name": "Test Type"})
    def test_it_detail(self):  self._test_401_403("/api/attendance/incident-types/999/")
    def test_it_list_auth(self):    self._test_auth("/api/attendance/incident-types/")
    def test_it_superuser(self):    self._test_superuser("/api/attendance/incident-types/")

    # --- SocioemotionalSkillViewSet ---
    def test_ss_list(self):    self._test_401_403("/api/attendance/socioemotional-skills/")
    def test_ss_create(self):  self._test_401_403("/api/attendance/socioemotional-skills/", "post", {"code": "EMP", "name": "Empatía"})
    def test_ss_detail(self):  self._test_401_403("/api/attendance/socioemotional-skills/999/")
    def test_ss_list_auth(self):    self._test_auth("/api/attendance/socioemotional-skills/")
    def test_ss_superuser(self):    self._test_superuser("/api/attendance/socioemotional-skills/")

    # --- SkillEvaluationViewSet ---
    def test_se_list(self):    self._test_401_403("/api/attendance/skill-evaluations/")
    def test_se_detail(self):  self._test_401_403("/api/attendance/skill-evaluations/999/")
    def test_se_list_auth(self):    self._test_auth("/api/attendance/skill-evaluations/")
    def test_se_superuser(self):    self._test_superuser("/api/attendance/skill-evaluations/")

    # --- AttendanceStatusViewSet ---
    def test_att_status_list(self):    self._test_401_403("/api/attendance/attendance-statuses/")
    def test_att_status_create(self):  self._test_401_403("/api/attendance/attendance-statuses/", "post", {"code": "P", "name": "Presente"})
    def test_att_status_detail(self):  self._test_401_403("/api/attendance/attendance-statuses/999/")
    def test_att_status_list_auth(self):    self._test_auth("/api/attendance/attendance-statuses/")
    def test_att_status_superuser(self):    self._test_superuser("/api/attendance/attendance-statuses/")
