from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.iam.models import Permission, Role, RolePermission, UserRole
from apps.core.constants.permissions import people as perms
from apps.core.tests.helpers import create_test_user


class PeoplePermissionsTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user_no_perm = create_test_user(
            email="no_perm_people@test.com", dni="4000000001",
            names="No", last_names="Perm",
        )
        self.user_with_perm = create_test_user(
            email="with_perm_people@test.com", dni="4000000002",
            names="With", last_names="Perm",
        )
        self.superuser = create_test_user(
            email="admin_people@test.com", dni="4000000000",
            names="Admin", last_names="People", is_superuser=True,
        )

        perm_codes = [
            perms.VIEW_DOCUMENT_TYPE, perms.CREATE_DOCUMENT_TYPE,
            perms.UPDATE_DOCUMENT_TYPE, perms.DELETE_DOCUMENT_TYPE,
            perms.VIEW_PERSON, perms.CREATE_PERSON,
            perms.UPDATE_PERSON, perms.DELETE_PERSON,
        ]
        role = Role.objects.create(name="People Test Role")
        for code in perm_codes:
            p, _ = Permission.objects.get_or_create(code=code, defaults={"module": "people"})
            RolePermission.objects.create(role=role, permission=p)
        UserRole.objects.create(user=self.user_with_perm, role=role)

    def _test_401_403(self, url, method="get", data=None):
        resp = getattr(self.client, method)(url, data or {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED, f"Expected 401 for {method} {url}")
        self.client.force_authenticate(user=self.user_no_perm)
        resp = getattr(self.client, method)(url, data or {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN, f"Expected 403 for {method} {url}")
        self.client.force_authenticate(user=None)

    def _test_auth(self, url):
        self.client.force_authenticate(user=self.user_with_perm)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def _test_superuser(self, url):
        self.client.force_authenticate(user=self.superuser)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # --- DocumentTypeViewSet ---
    def test_doc_type_list(self):    self._test_401_403("/api/people/document-types/")
    def test_doc_type_create(self):  self._test_401_403("/api/people/document-types/", "post", {"code": "X", "name": "Test"})
    def test_doc_type_detail(self):  self._test_401_403("/api/people/document-types/999/")
    def test_doc_type_update(self):  self._test_401_403("/api/people/document-types/999/", "patch", {"name": "X"})
    def test_doc_type_delete(self):  self._test_401_403("/api/people/document-types/999/", "delete")
    def test_doc_type_list_auth(self):    self._test_auth("/api/people/document-types/")
    def test_doc_type_superuser(self):    self._test_superuser("/api/people/document-types/")

    # --- PersonViewSet ---
    def test_person_list(self):    self._test_401_403("/api/people/persons/")
    def test_person_create(self):  self._test_401_403("/api/people/persons/", "post", {"document_number": "X", "names": "T", "last_names": "T"})
    def test_person_detail(self):  self._test_401_403("/api/people/persons/999/")
    def test_person_update(self):  self._test_401_403("/api/people/persons/999/", "patch", {"names": "X"})
    def test_person_delete(self):  self._test_401_403("/api/people/persons/999/", "delete")
    def test_person_list_auth(self):    self._test_auth("/api/people/persons/")
    def test_person_superuser(self):    self._test_superuser("/api/people/persons/")
