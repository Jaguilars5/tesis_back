from django.test import TestCase
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from rest_framework.views import APIView
from apps.core.api.exceptions import custom_exception_handler


class CustomExceptionHandlerTest(TestCase):
    """Tests para custom_exception_handler"""

    def setUp(self):
        self.view = APIView()
        self.context = {"view": self.view}

    def test_validation_error(self):
        exc = ValidationError({"field": ["This field is required."]})
        response = custom_exception_handler(exc, self.context)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data["ok"])
        self.assertIn("data", response.data)
        self.assertIn("msg", response.data)

    def test_permission_denied(self):
        exc = PermissionDenied()
        response = custom_exception_handler(exc, self.context)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.data["ok"])

    def test_not_found(self):
        exc = NotFound()
        response = custom_exception_handler(exc, self.context)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.data["ok"])

    def test_unhandled_exception(self):
        exc = ValueError("Unexpected error")
        response = custom_exception_handler(exc, self.context)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 500)
        self.assertFalse(response.data["ok"])
        self.assertEqual(response.data["data"], {})
        self.assertIn("Error interno del servidor", response.data["msg"])
