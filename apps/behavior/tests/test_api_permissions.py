from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.iam.models import Permission, Role, RolePermission, UserRole
from apps.core.constants.permissions import behavior
from apps.core.tests.helpers import create_test_user


class BehaviorPermissionsTest(TestCase):
    """Verifica RBAC para cada ViewSet de behavior."""

    def setUp(self):
        self.client = APIClient()

        self.user_no_perm = create_test_user(
            email="no_perm_beh@test.com", dni="6000000001",
            names="No", last_names="Perm",
        )
        self.user_with_perm = create_test_user(
            email="with_perm_beh@test.com", dni="6000000002",
            names="With", last_names="Perm",
        )
        self.superuser = create_test_user(
            email="admin_beh@test.com", dni="6000000000",
            names="Admin", last_names="Beh", is_superuser=True,
        )

        perm_codes = [
            behavior.VIEW_CONDUCT_INCIDENT, behavior.CREATE_CONDUCT_INCIDENT, behavior.UPDATE_CONDUCT_INCIDENT, behavior.DELETE_CONDUCT_INCIDENT,
            behavior.VIEW_BEHAVIOR_EVALUATION, behavior.CREATE_BEHAVIOR_EVALUATION, behavior.UPDATE_BEHAVIOR_EVALUATION, behavior.DELETE_BEHAVIOR_EVALUATION,
            behavior.VIEW_INCIDENT_TYPE, behavior.CREATE_INCIDENT_TYPE, behavior.UPDATE_INCIDENT_TYPE, behavior.DELETE_INCIDENT_TYPE,
            behavior.VIEW_SOCIOEMOTIONAL_SKILL, behavior.CREATE_SOCIOEMOTIONAL_SKILL, behavior.UPDATE_SOCIOEMOTIONAL_SKILL, behavior.DELETE_SOCIOEMOTIONAL_SKILL,
            behavior.VIEW_SKILL_EVALUATION, behavior.CREATE_SKILL_EVALUATION, behavior.UPDATE_SKILL_EVALUATION, behavior.DELETE_SKILL_EVALUATION,
            behavior.VIEW_DIAGNOSTIC_EVALUATION, behavior.CREATE_DIAGNOSTIC_EVALUATION, behavior.UPDATE_DIAGNOSTIC_EVALUATION, behavior.DELETE_DIAGNOSTIC_EVALUATION,
        ]
        role = Role.objects.create(name="Behavior Test Role", code="ADMIN")
        for code in perm_codes:
            p, _ = Permission.objects.get_or_create(code=code, defaults={"module": "behavior"})
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

    # --- ConductIncidentViewSet ---
    def test_ci_list(self):    self._test_401_403("/api/behavior/conduct-incidents/")
    def test_ci_create(self):  self._test_401_403("/api/behavior/conduct-incidents/", "post", {"incident_date": "2025-01-01", "severity": 1})
    def test_ci_detail(self):  self._test_401_403("/api/behavior/conduct-incidents/999/")
    def test_ci_list_auth(self):    self._test_auth("/api/behavior/conduct-incidents/")
    def test_ci_superuser(self):    self._test_superuser("/api/behavior/conduct-incidents/")

    # --- BehaviorEvaluationViewSet ---
    def test_be_list(self):    self._test_401_403("/api/behavior/behavior-evaluations/")
    def test_be_detail(self):  self._test_401_403("/api/behavior/behavior-evaluations/999/")
    def test_be_list_auth(self):    self._test_auth("/api/behavior/behavior-evaluations/")
    def test_be_superuser(self):    self._test_superuser("/api/behavior/behavior-evaluations/")

    # --- IncidentTypeViewSet ---
    def test_it_list(self):    self._test_401_403("/api/behavior/incident-types/")
    def test_it_create(self):  self._test_401_403("/api/behavior/incident-types/", "post", {"code": "TEST", "name": "Test Type"})
    def test_it_detail(self):  self._test_401_403("/api/behavior/incident-types/999/")
    def test_it_list_auth(self):    self._test_auth("/api/behavior/incident-types/")
    def test_it_superuser(self):    self._test_superuser("/api/behavior/incident-types/")

    # --- SocioemotionalSkillViewSet ---
    def test_ss_list(self):    self._test_401_403("/api/behavior/socioemotional-skills/")
    def test_ss_create(self):  self._test_401_403("/api/behavior/socioemotional-skills/", "post", {"code": "EMP", "name": "Empatía"})
    def test_ss_detail(self):  self._test_401_403("/api/behavior/socioemotional-skills/999/")
    def test_ss_list_auth(self):    self._test_auth("/api/behavior/socioemotional-skills/")
    def test_ss_superuser(self):    self._test_superuser("/api/behavior/socioemotional-skills/")

    # --- SkillEvaluationViewSet ---
    def test_se_list(self):    self._test_401_403("/api/behavior/skill-evaluations/")
    def test_se_detail(self):  self._test_401_403("/api/behavior/skill-evaluations/999/")
    def test_se_list_auth(self):    self._test_auth("/api/behavior/skill-evaluations/")
    def test_se_superuser(self):    self._test_superuser("/api/behavior/skill-evaluations/")

    # --- DiagnosticEvaluationViewSet ---
    def test_de_list(self):    self._test_401_403("/api/behavior/diagnostic-evaluations/")
    def test_de_create(self):  self._test_401_403("/api/behavior/diagnostic-evaluations/", "post", {"application_date": "2025-01-01"})
    def test_de_detail(self):  self._test_401_403("/api/behavior/diagnostic-evaluations/999/")
    def test_de_list_auth(self):    self._test_auth("/api/behavior/diagnostic-evaluations/")
    def test_de_superuser(self):    self._test_superuser("/api/behavior/diagnostic-evaluations/")