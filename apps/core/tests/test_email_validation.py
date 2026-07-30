import json
from unittest import mock

from django.test import SimpleTestCase, override_settings

from apps.core.email_validation import HunterEmailVerifier, is_email_deliverable


class _FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class HunterEmailVerifierTests(SimpleTestCase):
    @override_settings(HUNTER_API_KEY="", HUNTER_VALIDATE_EMAILS=True)
    def test_missing_api_key_allows_email(self):
        self.assertTrue(is_email_deliverable("user@example.com"))

    @override_settings(HUNTER_API_KEY="key", HUNTER_VALIDATE_EMAILS=True)
    @mock.patch("apps.core.email_validation.urlopen")
    def test_valid_email_is_allowed(self, mock_urlopen):
        mock_urlopen.return_value = _FakeResponse(
            {"data": {"status": "valid", "score": 95, "disposable": False}}
        )

        result = HunterEmailVerifier().verify("user@example.com")

        self.assertTrue(result.is_deliverable)

    @override_settings(HUNTER_API_KEY="key", HUNTER_VALIDATE_EMAILS=True)
    @mock.patch("apps.core.email_validation.urlopen")
    def test_invalid_email_is_blocked(self, mock_urlopen):
        mock_urlopen.return_value = _FakeResponse(
            {"data": {"status": "invalid", "score": 5, "disposable": False}}
        )

        result = HunterEmailVerifier().verify("bad@example.com")

        self.assertFalse(result.is_deliverable)

    @override_settings(HUNTER_API_KEY="key", HUNTER_VALIDATE_EMAILS=True)
    @mock.patch("apps.core.email_validation.urlopen")
    def test_unknown_low_score_is_blocked(self, mock_urlopen):
        mock_urlopen.return_value = _FakeResponse(
            {"data": {"status": "unknown", "score": 30, "disposable": False}}
        )

        result = HunterEmailVerifier().verify("maybe@example.com")

        self.assertFalse(result.is_deliverable)
