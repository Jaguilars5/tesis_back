from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.iam.models import Permission, Role, RolePermission, UserRole
from apps.core.constants.permissions import configuration as perms
from apps.core.tests.helpers import create_test_user


class ConfigurationPermissionsTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user_no_perm = create_test_user(
            email="no_perm_config@test.com", dni="9000000001",
            names="No", last_names="Perm",
        )
        self.user_with_perm = create_test_user(
            email="with_perm_config@test.com", dni="9000000002",
            names="With", last_names="Perm",
        )
        self.superuser = create_test_user(
            email="admin_config@test.com", dni="9000000000",
            names="Admin", last_names="Config", is_superuser=True,
        )

        perm_codes = [
            perms.VIEW_SYSTEM_CONFIG, perms.CREATE_SYSTEM_CONFIG,
            perms.UPDATE_SYSTEM_CONFIG, perms.DELETE_SYSTEM_CONFIG,
        ]
        role = Role.objects.create(name="Config Test Role")
        for code in perm_codes:
            p, _ = Permission.objects.get_or_create(code=code, defaults={"module": "configuration"})
            RolePermission.objects.create(role=role, permission=p)
        UserRole.objects.create(user=self.user_with_perm, role=role)

    def _test_401_403(self, url, method="get", data=None):
        resp = getattr(self.client, method)(url, data or {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(user=self.user_no_perm)
        resp = getattr(self.client, method)(url, data or {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=None)

    def _test_auth(self, url):
        self.client.force_authenticate(user=self.user_with_perm)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def _test_superuser(self, url):
        self.client.force_authenticate(user=self.superuser)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # --- SystemConfigViewSet ---
    def test_config_list(self):    self._test_401_403("/api/configuration/system-config/")
    def test_config_create(self):  self._test_401_403("/api/configuration/system-config/", "post", {"key": "X", "value": "Y"})
    def test_config_detail(self):  self._test_401_403("/api/configuration/system-config/999/")
    def test_config_update(self):  self._test_401_403("/api/configuration/system-config/999/", "patch", {"value": "X"})
    def test_config_delete(self):  self._test_401_403("/api/configuration/system-config/999/", "delete")
    def test_config_list_auth(self):    self._test_auth("/api/configuration/system-config/")
    def test_config_superuser(self):    self._test_superuser("/api/configuration/system-config/")
