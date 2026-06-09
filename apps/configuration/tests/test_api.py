from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.iam.models import Role
from apps.core.tests.helpers import create_test_user
from ..models import SystemConfig

User = get_user_model()


class SystemConfigAPITest(APITestCase):
    def setUp(self):
        self.role = Role.objects.create(name="Admin")
        self.user = create_test_user(
            email="config@test.com", dni="8000000001",
            names="Config", last_names="Test", is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.config = SystemConfig.objects.create(
            key="SITE_NAME", value="Mi Colegio"
        )
        self.url = "/api/configuration/system-config/"

    def test_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):
        data = {"key": "MAX_USERS", "value": "100"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve(self):
        response = self.client.get(f"{self.url}{self.config.key}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update(self):
        data = {"value": "Nuevo Colegio"}
        response = self.client.patch(f"{self.url}{self.config.key}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete(self):
        response = self.client.delete(f"{self.url}{self.config.key}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
