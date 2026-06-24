from django.test import TestCase
from django.conf import settings


class JWTConfigTestCase(TestCase):
    def test_access_token_lifetime(self):
        from config.settings.base import SIMPLE_JWT

        expected = settings.JWT_ACCESS_EXPIRE_MINUTES
        self.assertEqual(
            SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(),
            expected * 60,
        )

    def test_refresh_tokens_rotate(self):
        from config.settings.base import SIMPLE_JWT

        self.assertTrue(SIMPLE_JWT["ROTATE_REFRESH_TOKENS"])
        self.assertTrue(SIMPLE_JWT["BLACKLIST_AFTER_ROTATION"])
