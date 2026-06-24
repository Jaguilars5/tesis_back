from rest_framework.test import APITestCase
from rest_framework import status
from apps.core.tests.helpers import create_test_user


class AcademicGradeAPITest(APITestCase):
    def setUp(self):
        self.user = create_test_user(
            email="grade@test.com", dni="9999999999",
            names="Grade", last_names="Tester", is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/institutions/academic-grades/"

    def test_list_empty(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
