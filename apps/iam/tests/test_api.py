from django.test import TestCase
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIClient
from rest_framework import status

from apps.iam.models import User, Role, Permission, UserRole


class PermissionAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="admin123",
        )
        self.client.force_authenticate(user=self.user)

    def test_list_permissions_empty(self):
        response = self.client.get("/api/iam/permissions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_permission(self):
        data = {"code": "test.view_test", "description": "Test permission", "module": "test"}
        response = self.client.post("/api/iam/permissions/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_permission_duplicate(self):
        Permission.objects.create(code="test.view_test", module="test")
        data = {"code": "test.view_test", "description": "Duplicate", "module": "test"}
        response = self.client.post("/api/iam/permissions/", data, format="json")
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY])

    def test_list_permissions_with_data(self):
        Permission.objects.create(code="test.view_test", module="test")
        response = self.client.get("/api/iam/permissions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_bulk_create_permissions(self):
        data = {
            "permissions": [
                {"code": "test.view_one", "module": "test"},
                {"code": "test.view_two", "module": "test"},
            ]
        }
        response = self.client.post("/api/iam/permissions/bulk-create/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_by_module(self):
        Permission.objects.create(code="test.view_test", module="test")
        response = self.client.get("/api/iam/permissions/by-module/?module=test")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_by_module_missing_param(self):
        response = self.client.get("/api/iam/permissions/by-module/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_response_format(self):
        response = self.client.get("/api/iam/permissions/")
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)


class RoleAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="admin123",
        )
        self.client.force_authenticate(user=self.user)

    def test_create_role(self):
        data = {"name": "Test Role"}
        response = self.client.post("/api/iam/roles/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_role_duplicate(self):
        Role.objects.create(name="Test Role")
        data = {"name": "Test Role"}
        response = self.client.post("/api/iam/roles/", data, format="json")
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY])

    def test_list_roles(self):
        Role.objects.create(name="Role 1")
        response = self.client.get("/api/iam/roles/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_permission_to_role(self):
        role = Role.objects.create(name="Test Role")
        perm = Permission.objects.create(code="test.view_test", module="test")
        response = self.client.post(
            f"/api/iam/roles/{role.id}/add-permission/",
            {"permission_code": "test.view_test"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="admin123",
        )
        self.client.force_authenticate(user=self.admin)
        self.role = Role.objects.create(name="Test Role", code="TEST")

    def test_create_user(self):
        data = {
            "document_number": "12345678",
            "names": "Test",
            "last_names": "User",
            "email": "test@example.com",
            "password": "testpass123",
            "role_id": self.role.id,
        }
        response = self.client.post("/api/iam/users/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_duplicate_email(self):
        data = {
            "document_number": "12345678",
            "names": "Test",
            "last_names": "User",
            "email": "test@example.com",
            "password": "testpass123",
            "role_id": self.role.id,
        }
        self.client.post("/api/iam/users/", data, format="json")
        response = self.client.post("/api/iam/users/", data, format="json")
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY])

    def test_list_users(self):
        response = self.client.get("/api/iam/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_returns_role_code_and_role_id(self):
        from datetime import date
        from apps.people.models import Person, DocumentType

        doc_type = DocumentType.objects.get_or_create(
            code="CC", defaults={"name": "CÃ©dula de CiudadanÃ­a"}
        )[0]
        person = Person.objects.create(
            document_type=doc_type,
            document_number="ROLE-001",
            names="Role",
            last_names="Contract",
            email="role.contract@test.com",
            birth_date=date(2000, 1, 1),
        )
        user = User.objects.create(username="rolecontract", person=person)
        UserRole.objects.create(user=user, role=self.role)

        response = self.client.get(f"/api/iam/users/{user.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = response.data["data"] if "data" in response.data else response.data
        self.assertEqual(payload["role"], self.role.code)
        self.assertEqual(payload["role_id"], self.role.id)
        self.assertIsInstance(payload["role"], str)

    def test_change_password(self):
        from datetime import date
        from apps.people.models import Person, DocumentType
        doc_type = DocumentType.objects.get_or_create(
            code="CC", defaults={"name": "Cédula de Ciudadanía"}
        )[0]
        new_person = Person.objects.create(
            document_type=doc_type,
            document_number="CHPASS-001",
            names="Change",
            last_names="Password",
            email="changepass@test.com",
            birth_date=date(2000, 1, 1),
        )
        user = User.objects.create(
            username="testuser",
            person=new_person,
        )
        user.set_password("OldPass123!Segura")
        user.save()
        response = self.client.post(
            f"/api/iam/users/{user.id}/change-password/",
            {"new_password": "NewStrongPass!2024"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_request_sends_email(self):
        from datetime import date
        from apps.people.models import Person, DocumentType

        self.client.logout()
        doc_type = DocumentType.objects.get_or_create(
            code="CC", defaults={"name": "CÃ©dula de CiudadanÃ­a"}
        )[0]
        person = Person.objects.create(
            document_type=doc_type,
            document_number="RESET-001",
            names="Reset",
            last_names="User",
            email="reset@test.com",
            birth_date=date(2000, 1, 1),
        )
        User.objects.create_user(
            username="resetuser",
            person=person,
            password="OldPass123!Segura",
        )

        response = self.client.post(
            "/api/iam/password-reset/request/",
            {"identifier": "reset@test.com"},
            format="json",
            HTTP_ORIGIN="http://localhost:5173",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/reset-password/", mail.outbox[0].body)

    def test_password_reset_confirm_changes_password(self):
        from datetime import date
        from apps.people.models import Person, DocumentType

        self.client.logout()
        doc_type = DocumentType.objects.get_or_create(
            code="CC", defaults={"name": "CÃ©dula de CiudadanÃ­a"}
        )[0]
        person = Person.objects.create(
            document_type=doc_type,
            document_number="RESET-002",
            names="Reset",
            last_names="Confirm",
            email="reset-confirm@test.com",
            birth_date=date(2000, 1, 1),
        )
        user = User.objects.create_user(
            username="resetconfirm",
            person=person,
            password="OldPass123!Segura",
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        response = self.client.post(
            "/api/iam/password-reset/confirm/",
            {
                "uid": uid,
                "token": token,
                "new_password": "NewStrongPass!2026",
            },
            format="json",
        )

        user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(user.check_password("NewStrongPass!2026"))
        self.assertFalse(user.must_change_password)
