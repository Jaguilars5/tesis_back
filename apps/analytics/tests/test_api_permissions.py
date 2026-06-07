from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Permission, Role, RolePermission, UserRole
from apps.core.constants.permissions import analytics as perms
from apps.core.tests.helpers import create_test_user


class AnalyticsPermissionsTest(TestCase):
    """Verifica RBAC para cada ViewSet de analytics."""

    def setUp(self):
        self.client = APIClient()

        self.user_no_perm = create_test_user(
            email="no_perm_an@test.com", dni="4000000001",
            names="No", last_names="Perm",
        )
        self.user_with_perm = create_test_user(
            email="with_perm_an@test.com", dni="4000000002",
            names="With", last_names="Perm", user_type="ADMIN",
        )
        self.superuser = create_test_user(
            email="admin_an@test.com", dni="4000000000",
            names="Admin", last_names="An", is_superuser=True,
        )

        perm_codes = [
            perms.VIEW_RISK_SCORE,
            perms.VIEW_FEATURE_SNAPSHOT,
            perms.VIEW_RISK_FACTOR,
            perms.VIEW_STUDENT_RISK_FACTOR,
            perms.VIEW_EARLY_ALERT, perms.CREATE_EARLY_ALERT,
            perms.UPDATE_EARLY_ALERT, perms.DELETE_EARLY_ALERT,
        ]
        role = Role.objects.create(name="Analytics Test Role")
        for code in perm_codes:
            p, _ = Permission.objects.get_or_create(code=code, defaults={"module": "analytics"})
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

    # --- StudentRiskScoreViewSet ---
    def test_risk_score_list(self):    self._test_401_403("/api/analytics/student-risk-scores/")
    def test_risk_score_detail(self):  self._test_401_403("/api/analytics/student-risk-scores/999/")
    def test_risk_score_list_auth(self):    self._test_auth("/api/analytics/student-risk-scores/")
    def test_risk_score_superuser(self):    self._test_superuser("/api/analytics/student-risk-scores/")

    # --- StudentFeatureSnapshotViewSet ---
    def test_snapshot_list(self):    self._test_401_403("/api/analytics/feature-snapshots/")
    def test_snapshot_detail(self):  self._test_401_403("/api/analytics/feature-snapshots/999/")
    def test_snapshot_list_auth(self):    self._test_auth("/api/analytics/feature-snapshots/")
    def test_snapshot_superuser(self):    self._test_superuser("/api/analytics/feature-snapshots/")

    # --- RiskFactorViewSet ---
    def test_risk_factor_list(self):    self._test_401_403("/api/analytics/risk-factors/")
    def test_risk_factor_detail(self):  self._test_401_403("/api/analytics/risk-factors/999/")
    def test_risk_factor_list_auth(self):    self._test_auth("/api/analytics/risk-factors/")
    def test_risk_factor_superuser(self):    self._test_superuser("/api/analytics/risk-factors/")

    # --- StudentRiskFactorViewSet ---
    def test_stu_risk_factor_list(self):    self._test_401_403("/api/analytics/student-risk-factors/")
    def test_stu_risk_factor_detail(self):  self._test_401_403("/api/analytics/student-risk-factors/999/")
    def test_stu_risk_factor_list_auth(self):    self._test_auth("/api/analytics/student-risk-factors/")
    def test_stu_risk_factor_superuser(self):    self._test_superuser("/api/analytics/student-risk-factors/")

    # --- EarlyAlertViewSet ---
    def test_early_alert_list(self):    self._test_401_403("/api/analytics/early-alerts/")
    def test_early_alert_create(self):  self._test_401_403("/api/analytics/early-alerts/", "post", {"description": "Test", "alert_type": "low_attendance", "urgency_level": "high"})
    def test_early_alert_detail(self):  self._test_401_403("/api/analytics/early-alerts/999/")
    def test_early_alert_list_auth(self):    self._test_auth("/api/analytics/early-alerts/")
    def test_early_alert_superuser(self):    self._test_superuser("/api/analytics/early-alerts/")
