from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.iam.models import Role
from apps.core.tests.helpers import create_test_user
from ..models import DocumentType

User = get_user_model()


class DocumentTypeAPITest(APITestCase):
    def setUp(self):
        self.role = Role.objects.create(name="Admin")
        self.user = create_test_user(
            email="doc_type@test.com", dni="3000000001",
            names="Doc", last_names="Type", is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.doc_type = DocumentType.objects.create(code="TI", name="Tarjeta Identidad")
        self.url = "/api/people/document-types/"

    def test_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):
        data = {"code": "PAS", "name": "Pasaporte"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve(self):
        response = self.client.get(f"{self.url}{self.doc_type.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update(self):
        data = {"name": "Cédula Modificada"}
        response = self.client.patch(f"{self.url}{self.doc_type.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete(self):
        response = self.client.delete(f"{self.url}{self.doc_type.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class PersonAPITest(APITestCase):
    def setUp(self):
        self.role = Role.objects.create(name="Admin")
        self.doc_type = DocumentType.objects.create(code="CC", name="Cédula")
        self.user = create_test_user(
            email="person_api@test.com", dni="3000000002",
            names="Person", last_names="API", is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/people/persons/"

    def test_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):
        data = {
            "document_type": self.doc_type.id,
            "document_number": "0987654321",
            "names": "María",
            "last_names": "Gómez",
            "email": "maria@example.com",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve(self):
        from ..models import Person
        person = Person.objects.create(
            document_type=self.doc_type, document_number="1111111111",
            names="Test", last_names="Person",
        )
        response = self.client.get(f"{self.url}{person.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update(self):
        from ..models import Person
        person = Person.objects.create(
            document_type=self.doc_type, document_number="2222222222",
            names="Test", last_names="Person",
        )
        data = {"names": "Updated"}
        response = self.client.patch(f"{self.url}{person.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete(self):
        from ..models import Person
        person = Person.objects.create(
            document_type=self.doc_type, document_number="3333333333",
            names="Test", last_names="Person",
        )
        response = self.client.delete(f"{self.url}{person.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
