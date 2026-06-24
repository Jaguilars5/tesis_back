from rest_framework.test import APITestCase
from rest_framework import status
from apps.academic.period_type.infrastructure.models import PeriodType
from apps.core.tests.helpers import create_test_user


class PeriodTypeAPITest(APITestCase):
    def setUp(self):
        self.user = create_test_user(
            email="pt@test.com", dni="2222222222",
            names="PT", last_names="Tester", is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/academic/period-types/"

    def test_create(self):
        data = {"code": "TRIM", "name": "Trimestre", "divisions_per_year": 3}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
