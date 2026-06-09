from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.iam.models import Permission, Role, RolePermission, UserRole
from apps.core.constants.permissions import integration as perms
from apps.core.tests.helpers import create_test_user


class IntegrationPermissionsTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user_no_perm = create_test_user(
            email="no_perm_int@test.com", dni="6000000001",
            names="No", last_names="Perm",
        )
        self.user_with_perm = create_test_user(
            email="with_perm_int@test.com", dni="6000000002",
            names="With", last_names="Perm",
        )
        self.superuser = create_test_user(
            email="admin_int@test.com", dni="6000000000",
            names="Admin", last_names="Int", is_superuser=True,
        )

        perm_codes = [
            perms.VIEW_SYNC_QUEUE, perms.CREATE_SYNC_QUEUE,
            perms.UPDATE_SYNC_QUEUE, perms.DELETE_SYNC_QUEUE,
            perms.VIEW_SYNC_OPERATION, perms.CREATE_SYNC_OPERATION,
            perms.UPDATE_SYNC_OPERATION, perms.DELETE_SYNC_OPERATION,
            perms.VIEW_SYNC_STATUS, perms.CREATE_SYNC_STATUS,
            perms.UPDATE_SYNC_STATUS, perms.DELETE_SYNC_STATUS,
        ]
        role = Role.objects.create(name="Integration Test Role")
        for code in perm_codes:
            p, _ = Permission.objects.get_or_create(code=code, defaults={"module": "integration"})
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

    # --- SyncOperationViewSet ---
    def test_op_list(self):    self._test_401_403("/api/integration/sync-operations/")
    def test_op_create(self):  self._test_401_403("/api/integration/sync-operations/", "post", {"code": "X", "name": "Y"})
    def test_op_detail(self):  self._test_401_403("/api/integration/sync-operations/999/")
    def test_op_update(self):  self._test_401_403("/api/integration/sync-operations/999/", "patch", {"name": "X"})
    def test_op_delete(self):  self._test_401_403("/api/integration/sync-operations/999/", "delete")
    def test_op_list_auth(self):    self._test_auth("/api/integration/sync-operations/")
    def test_op_superuser(self):    self._test_superuser("/api/integration/sync-operations/")

    # --- SyncStatusViewSet ---
    def test_st_list(self):    self._test_401_403("/api/integration/sync-statuses/")
    def test_st_create(self):  self._test_401_403("/api/integration/sync-statuses/", "post", {"code": "X", "name": "Y"})
    def test_st_detail(self):  self._test_401_403("/api/integration/sync-statuses/999/")
    def test_st_update(self):  self._test_401_403("/api/integration/sync-statuses/999/", "patch", {"name": "X"})
    def test_st_delete(self):  self._test_401_403("/api/integration/sync-statuses/999/", "delete")
    def test_st_list_auth(self):    self._test_auth("/api/integration/sync-statuses/")
    def test_st_superuser(self):    self._test_superuser("/api/integration/sync-statuses/")

    # --- SyncQueueViewSet ---
    def test_sq_list(self):    self._test_401_403("/api/integration/sync-queue/")
    def test_sq_create(self):  self._test_401_403("/api/integration/sync-queue/", "post", {"source_table": "X", "record_uuid": "00000000-0000-0000-0000-000000000000"})
    def test_sq_detail(self):  self._test_401_403("/api/integration/sync-queue/999/")
    def test_sq_update(self):  self._test_401_403("/api/integration/sync-queue/999/", "patch", {"source_table": "X"})
    def test_sq_delete(self):  self._test_401_403("/api/integration/sync-queue/999/", "delete")
    def test_sq_list_auth(self):    self._test_auth("/api/integration/sync-queue/")
    def test_sq_superuser(self):    self._test_superuser("/api/integration/sync-queue/")
