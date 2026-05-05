from django.test import TestCase
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class ThrottlingTestCase(TestCase):
    def test_anon_throttle_rate_parsed(self):
        throttle = AnonRateThrottle()
        throttle.rate = "100/day"
        num_requests, duration = throttle.parse_rate(throttle.rate)
        self.assertEqual(num_requests, 100)
        self.assertEqual(duration, 86400)

    def test_user_throttle_rate_parsed(self):
        throttle = UserRateThrottle()
        throttle.rate = "1000/day"
        num_requests, duration = throttle.parse_rate(throttle.rate)
        self.assertEqual(num_requests, 1000)
        self.assertEqual(duration, 86400)

    def test_login_throttle_rate_parsed(self):
        from rest_framework.throttling import ScopedRateThrottle

        throttle = ScopedRateThrottle()
        throttle.rate = "10/hour"
        num_requests, duration = throttle.parse_rate(throttle.rate)
        self.assertEqual(num_requests, 10)
        self.assertEqual(duration, 3600)

    def test_config_anon_rate(self):
        from django.conf import settings

        rates = settings.REST_FRAMEWORK.get("DEFAULT_THROTTLE_RATES", {})
        self.assertIn("anon", rates)
        self.assertEqual(rates["anon"], "100/day")

    def test_config_user_rate(self):
        from django.conf import settings

        rates = settings.REST_FRAMEWORK.get("DEFAULT_THROTTLE_RATES", {})
        self.assertIn("user", rates)
        self.assertEqual(rates["user"], "1000/day")

    def test_config_login_rate(self):
        from django.conf import settings

        rates = settings.REST_FRAMEWORK.get("DEFAULT_THROTTLE_RATES", {})
        self.assertIn("login", rates)
        self.assertEqual(rates["login"], "10/hour")

    def test_throttle_classes_configured(self):
        from django.conf import settings

        classes = settings.REST_FRAMEWORK.get("DEFAULT_THROTTLE_CLASSES", [])
        self.assertIn(
            "rest_framework.throttling.AnonRateThrottle", classes
        )
        self.assertIn(
            "rest_framework.throttling.UserRateThrottle", classes
        )
