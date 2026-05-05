from django.test import TestCase
from rest_framework import status


class OpenAPISchemaTestCase(TestCase):
    def test_schema_endpoint_returns_200(self):
        response = self.client.get("/api/schema/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_swagger_ui_endpoint_returns_200(self):
        response = self.client.get("/api/docs/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_redoc_endpoint_returns_200(self):
        response = self.client.get("/api/redoc/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
