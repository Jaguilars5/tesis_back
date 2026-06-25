from rest_framework.test import APITestCase
from rest_framework import status

from apps.core.tests.helpers import create_test_user

from ..infrastructure.models import PeriodType


class PeriodTypeAPITest(APITestCase):
    def setUp(self):
        self.user = create_test_user(
            email="pt@test.com", dni="2222222222",
            names="PT", last_names="Tester", is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/academic/period-types/"

    def test_list_empty(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_create(self):
        data = {"code": "TRIM", "name": "Trimestre", "divisions_per_year": 3}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["ok"])

    def test_get(self):
        obj = PeriodType.objects.create(code="QUIM", name="Quimestre", divisions_per_year=2)
        response = self.client.get(f"{self.url}{obj.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        self.assertEqual(response.data["data"]["code"], "QUIM")

    def test_update(self):
        obj = PeriodType.objects.create(code="TRIM", name="Trimestre", divisions_per_year=3)
        data = {"code": "SEM", "name": "Semestre", "divisions_per_year": 2}
        response = self.client.put(f"{self.url}{obj.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        self.assertEqual(response.data["data"]["code"], "SEM")

    def test_destroy(self):
        obj = PeriodType.objects.create(code="TMP", name="Temporal", divisions_per_year=1)
        response = self.client.delete(f"{self.url}{obj.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])

    def test_soft_delete(self):
        obj = PeriodType.objects.create(code="TRIM", name="Trimestre", divisions_per_year=3)
        response = self.client.post(f"{self.url}{obj.id}/soft-delete/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        self.assertFalse(response.data["data"]["is_active"])

    def test_permission_denied(self):
        user_no_perm = create_test_user(
            email="noperm@test.com", dni="3333333333",
            names="No", last_names="Perm", is_superuser=False,
        )
        self.client.force_authenticate(user=user_no_perm)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_search_by_name(self):
        PeriodType.objects.create(code="TRIM", name="Trimestre", divisions_per_year=3)
        PeriodType.objects.create(code="SEM", name="Semestre", divisions_per_year=2)
        response = self.client.get(f"{self.url}?search=Trim")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["code"], "TRIM")

    def test_filter_by_code_icontains(self):
        PeriodType.objects.create(code="TRIM", name="Trimestre", divisions_per_year=3)
        PeriodType.objects.create(code="SEM", name="Semestre", divisions_per_year=2)
        response = self.client.get(f"{self.url}?code=tri")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["code"], "TRIM")

    def test_create_duplicate_code(self):
        PeriodType.objects.create(code="TRIM", name="Trimestre", divisions_per_year=3)
        data = {"code": "TRIM", "name": "Otro Trimestre", "divisions_per_year": 3}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
