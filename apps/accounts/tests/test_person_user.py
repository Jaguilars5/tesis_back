from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.db import IntegrityError
from apps.accounts.models import Person, User, Role, UserRole
from apps.accounts.services.person_service import PersonService
from apps.core.tests.helpers import create_test_user
from apps.institutions.models import DocumentType


class PersonModelTest(TestCase):
    """Tests para el modelo Person."""

    def setUp(self):
        doc_type, _ = DocumentType.objects.get_or_create(
            code="CC", defaults={"name": "Cedula de Ciudadania"}
        )
        self.person = Person.objects.create(
            document_type=doc_type,
            document_number="1234567890",
            names="Juan",
            last_names="Perez",
            email="juan@example.com",
        )

    def test_create_person_directly(self):
        self.assertEqual(self.person.document_number, "1234567890")
        self.assertEqual(self.person.names, "Juan")
        self.assertEqual(self.person.last_names, "Perez")
        self.assertEqual(self.person.email, "juan@example.com")
        self.assertTrue(self.person.active)

    def test_person_str(self):
        self.assertEqual(str(self.person), "Juan Perez")

    def test_person_get_full_name(self):
        self.assertEqual(self.person.get_full_name(), "Juan Perez")

    def test_person_unique_document_number(self):
        doc_type, _ = DocumentType.objects.get_or_create(
            code="CC", defaults={"name": "Cedula de Ciudadania"}
        )
        with self.assertRaises(IntegrityError):
            Person.objects.create(
                document_type=doc_type,
                document_number="1234567890",
                names="Pedro",
                last_names="Garcia",
            )


class PersonServiceTest(TestCase):
    """Tests para PersonService."""

    def setUp(self):
        self.role = Role.objects.create(name="Docente")

    def test_create_person_with_user(self):
        person, user = PersonService.create_person_with_user(
            person_data={
                "document_number": "1111111111",
                "names": "Maria",
                "last_names": "Lopez",
                "email": "maria@example.com",
            },
            password="securepass123",
        )

        self.assertIsNotNone(person.id)
        self.assertEqual(person.names, "Maria")
        self.assertIsNotNone(user.id)
        self.assertEqual(user.email, "maria@example.com")
        self.assertTrue(user.check_password("securepass123"))

    def test_create_person_with_user_and_role(self):
        person, user = PersonService.create_person_with_user(
            person_data={
                "document_number": "2222222222",
                "names": "Carlos",
                "last_names": "Garcia",
                "email": "carlos@example.com",
            },
            password="pass12345",
        )
        UserRole.objects.create(user=user, role=self.role)

        self.assertEqual(user.user_roles.count(), 1)
        self.assertEqual(user.user_roles.first().role.name, "Docente")

    def test_create_person_with_student(self):
        person, student = PersonService.create_person_with_student(
            person_data={
                "document_number": "3333333333",
                "names": "Ana",
                "last_names": "Martinez",
                "email": "ana@example.com",
                "birth_date": None,
            },
            student_code="EST-001",
        )

        self.assertIsNotNone(person.id)
        self.assertIsNotNone(student.id)
        self.assertEqual(student.student_code, "EST-001")
        self.assertEqual(student.person.names, "Ana")

    def test_create_person_with_student_auto_code(self):
        person, student = PersonService.create_person_with_student(
            person_data={
                "document_number": "4444444444",
                "names": "Luis",
                "last_names": "Ramirez",
            },
        )

        self.assertIsNotNone(student.student_code)
        self.assertTrue(student.student_code.startswith("EST-"))

    def test_person_service_search(self):
        PersonService.create_person_with_user(
            person_data={
                "document_number": "5555555555",
                "names": "Searchable",
                "last_names": "Person",
                "email": "search@example.com",
            },
            password="pass",
        )

        results = PersonService.search_person(names="Searchable")
        self.assertEqual(results.count(), 1)

        results = PersonService.search_person(email="search@example.com")
        self.assertEqual(results.count(), 1)


class UserLoginTest(TestCase):
    """Tests para login usando email como USERNAME_FIELD."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_test_user(
            email="login@example.com",
            dni="9999999999",
            names="Login",
            last_names="User",
            password="test_password_123",
        )

    def test_user_login_with_email(self):
        response = self.client.post(
            "/api/accounts/login/",
            {"email": "login@example.com", "password": "test_password_123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_user_login_invalid_password(self):
        response = self.client.post(
            "/api/accounts/login/",
            {"email": "login@example.com", "password": "wrong_password"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_login_nonexistent_email(self):
        response = self.client.post(
            "/api/accounts/login/",
            {"email": "noexiste@example.com", "password": "test_password_123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
