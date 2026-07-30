from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password


class PasswordValidationTestCase(TestCase):
    def test_short_password_rejected(self):
        with self.assertRaises(ValidationError):
            validate_password("short1")

    def test_numeric_password_rejected(self):
        with self.assertRaises(ValidationError):
            validate_password("123456789012")

    def test_common_password_rejected(self):
        with self.assertRaises(ValidationError):
            validate_password("password123456")

    def test_valid_password_accepted(self):
        validate_password("MyStr0ng!Pass#2024")

    def test_underscore_is_accepted_with_minimum_length(self):
        validate_password("Clave_2026")
