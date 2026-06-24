from rest_framework.test import APITestCase
from rest_framework import status
from apps.academic.subject.infrastructure.models import Subject
from apps.core.tests.helpers import create_test_user


class SubjectAPITest(APITestCase):
    def setUp(self):
        self.user = create_test_user(
            email="subject@test.com", dni="1111111111",
            names="Subject", last_names="Tester", is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/academic/subjects/"

    def test_list(self):
        Subject.objects.create(name="Matemáticas", code="MAT-001")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):
        data = {"name": "Lengua", "code": "LEN-001"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve(self):
        subject = Subject.objects.create(name="Ciencias", code="CIE-001")
        response = self.client.get(f"{self.url}{subject.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update(self):
        subject = Subject.objects.create(name="Historia", code="HIS-001")
        data = {"name": "Historia Universal", "code": "HIS-001"}
        response = self.client.put(f"{self.url}{subject.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_soft_delete(self):
        subject = Subject.objects.create(name="Geografía", code="GEO-001")
        response = self.client.post(f"{self.url}{subject.id}/soft-delete/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Subject.objects.get(id=subject.id).is_active)
