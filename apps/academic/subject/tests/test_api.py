from rest_framework.test import APITestCase
from rest_framework import status

from apps.core.tests.helpers import create_test_user

from ..infrastructure.models import Subject


class SubjectAPITest(APITestCase):
    def setUp(self):
        self.user = create_test_user(
            email="subject@test.com", dni="1111111111",
            names="Subject", last_names="Tester", is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/academic/subjects/"

    def test_list_empty(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_list_with_data(self):
        Subject.objects.create(name="Matem\u00e1ticas", code="MAT-001")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create(self):
        data = {"name": "Lengua", "code": "LEN-001"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["ok"])

    def test_retrieve(self):
        subject = Subject.objects.create(name="Ciencias", code="CIE-001")
        response = self.client.get(f"{self.url}{subject.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        self.assertEqual(response.data["data"]["name"], "Ciencias")

    def test_update(self):
        subject = Subject.objects.create(name="Historia", code="HIS-001")
        data = {"name": "Historia Universal", "code": "HIS-001"}
        response = self.client.put(f"{self.url}{subject.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        self.assertEqual(response.data["data"]["name"], "Historia Universal")

    def test_destroy(self):
        subject = Subject.objects.create(name="Temporal", code="TMP-001")
        response = self.client.delete(f"{self.url}{subject.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])

    def test_soft_delete(self):
        subject = Subject.objects.create(name="Geografia", code="GEO-001")
        response = self.client.post(f"{self.url}{subject.id}/soft-delete/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        self.assertFalse(response.data["data"]["is_active"])

    def test_permission_denied(self):
        user_no_perm = create_test_user(
            email="noperm@test.com", dni="9999999999",
            names="No", last_names="Perm", is_superuser=False,
        )
        self.client.force_authenticate(user=user_no_perm)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_search_by_name(self):
        Subject.objects.create(name="Matem\u00e1ticas", code="MAT-001")
        Subject.objects.create(name="Lengua", code="LEN-001")
        response = self.client.get(f"{self.url}?search=Matem")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["code"], "MAT-001")

    def test_create_duplicate_code(self):
        Subject.objects.create(name="Matem\u00e1ticas", code="MAT-001")
        data = {"name": "Otra", "code": "MAT-001"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
