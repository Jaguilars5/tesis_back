"""
Tests de capa de Repositorios para el módulo accounts.
"""

from django.test import TestCase
from apps.iam.models import Person, User, Role, Permission, RolePermission
from apps.iam.repositories.user_repo import UserRepository
from apps.iam.repositories.permission_repo import PermissionRepository, RoleRepository
from apps.iam.repositories.person_repo import PersonRepository
from apps.core.tests.helpers import create_test_user


class UserRepositoryTest(TestCase):
    """Tests para UserRepository."""

    def setUp(self):
        self.user = create_test_user(email="juan@example.com", dni="1725556661")
        self.doc_type = self.user.person.document_type

    def test_get_by_id_exists(self):
        result = UserRepository.get_by_id(self.user.id)
        self.assertEqual(result, self.user)

    def test_get_by_id_not_exists(self):
        result = UserRepository.get_by_id(99999)
        self.assertIsNone(result)

    def test_get_by_email_exists(self):
        result = UserRepository.get_by_email("juan@example.com")
        self.assertEqual(result, self.user)

    def test_get_by_email_not_exists(self):
        result = UserRepository.get_by_email("notfound@example.com")
        self.assertIsNone(result)

    def test_get_by_dni_exists(self):
        result = UserRepository.get_by_dni("1725556661")
        self.assertEqual(result, self.user)

    def test_get_by_dni_not_exists(self):
        result = UserRepository.get_by_dni("0000000000")
        self.assertIsNone(result)

    def test_get_all_active(self):
        create_test_user(email="inactive@example.com", dni="1725556662", active=False)
        result = UserRepository.get_all_active()
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().email, "juan@example.com")

    def test_get_by_role(self):
        role = Role.objects.create(name="Docente")
        RolePermission.objects.create(
            role=role, permission=Permission.objects.create(code="test", module="test")
        )
        self.user.user_roles.create(role=role)
        result = UserRepository.get_by_role(role.id)
        self.assertEqual(result.count(), 1)

    def test_create(self):
        person = Person.objects.create(
            document_type=self.doc_type,
            document_number="1725556663",
            names="Pedro",
            last_names="García",
        )
        user = UserRepository.create(
            person=person,
            password="newpass123",
        )
        self.assertEqual(user.person, person)
        self.assertTrue(user.check_password("newpass123"))

    def test_update_email(self):
        updated = UserRepository.update(self.user, email="newemail@example.com")
        self.assertEqual(updated.email, "newemail@example.com")

    def test_update_ignores_disallowed_fields(self):
        UserRepository.update(
            self.user, email="newemail@example.com", is_superuser=True
        )
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_superuser)

    def test_delete_soft_deletes(self):
        UserRepository.delete(self.user)
        self.user.refresh_from_db()
        self.assertFalse(self.user.active)

    def test_bulk_create(self):
        persons = [
            Person.objects.create(
                document_type=self.doc_type,
                document_number=f"17255566{i}",
                names=f"Persona{i}",
                last_names="Test",
            )
            for i in range(3, 6)
        ]
        users = UserRepository.bulk_create(
            [
                {
                    "person": persons[0],
                    "email": "bulk1@example.com",
                    "password": "pass1",
                },
                {
                    "person": persons[1],
                    "email": "bulk2@example.com",
                    "password": "pass2",
                },
                {
                    "person": persons[2],
                    "email": "bulk3@example.com",
                    "password": "pass3",
                },
            ]
        )
        self.assertEqual(len(users), 3)

    def test_search_found(self):
        result = UserRepository.search("Juan")
        self.assertEqual(result.count(), 1)

    def test_search_not_found(self):
        result = UserRepository.search("xyz123")
        self.assertEqual(result.count(), 0)


class PermissionRepositoryTest(TestCase):
    """Tests para PermissionRepository."""

    def setUp(self):
        self.permission = Permission.objects.create(
            code="test.permission",
            description="Permiso de prueba",
            module="test",
        )

    def test_get_by_id_exists(self):
        result = PermissionRepository.get_by_id(self.permission.id)
        self.assertEqual(result, self.permission)

    def test_get_by_id_not_exists(self):
        result = PermissionRepository.get_by_id(99999)
        self.assertIsNone(result)

    def test_get_by_code_exists(self):
        result = PermissionRepository.get_by_code("test.permission")
        self.assertEqual(result, self.permission)

    def test_get_by_code_not_exists(self):
        result = PermissionRepository.get_by_code("not.exists")
        self.assertIsNone(result)

    def test_get_all(self):
        result = PermissionRepository.get_all()
        self.assertGreaterEqual(result.count(), 1)

    def test_get_by_module(self):
        Permission.objects.create(code="other.test", module="other")
        result = PermissionRepository.get_by_module("test")
        self.assertEqual(result.count(), 1)

    def test_create(self):
        perm = PermissionRepository.create(
            code="new.permission",
            description="Nuevo",
            module="test",
        )
        self.assertEqual(perm.code, "new.permission")

    def test_create_many(self):
        perms = PermissionRepository.create_many(
            [
                {"code": "bulk.1", "module": "test"},
                {"code": "bulk.2", "module": "test"},
            ]
        )
        self.assertEqual(len(perms), 2)

    def test_update(self):
        updated = PermissionRepository.update(
            self.permission,
            description="Actualizada",
            module="changed",
        )
        self.assertEqual(updated.description, "Actualizada")
        self.assertEqual(updated.module, "changed")

    def test_update_ignores_code(self):
        PermissionRepository.update(self.permission, code="changed.code")
        self.permission.refresh_from_db()
        self.assertEqual(self.permission.code, "test.permission")

    def test_delete(self):
        pid = self.permission.id
        PermissionRepository.delete(self.permission)
        self.assertFalse(Permission.objects.filter(id=pid).exists())

    def test_search(self):
        result = PermissionRepository.search("prueba")
        self.assertEqual(result.count(), 1)

    def test_search_not_found(self):
        result = PermissionRepository.search("xyz999")
        self.assertEqual(result.count(), 0)


class RoleRepositoryTest(TestCase):
    """Tests para RoleRepository."""

    def setUp(self):
        self.role = Role.objects.create(name="Docente", description="Rol de docente")
        self.permission = Permission.objects.create(
            code="test.permission", module="test"
        )

    def test_get_by_id_exists(self):
        result = RoleRepository.get_by_id(self.role.id)
        self.assertEqual(result, self.role)

    def test_get_by_id_not_exists(self):
        result = RoleRepository.get_by_id(99999)
        self.assertIsNone(result)

    def test_get_by_name_exists(self):
        result = RoleRepository.get_by_name("Docente")
        self.assertEqual(result, self.role)

    def test_get_by_name_not_exists(self):
        result = RoleRepository.get_by_name("NoExiste")
        self.assertIsNone(result)

    def test_get_all_active(self):
        Role.objects.create(name="Inactivo", active=False)
        result = RoleRepository.get_all_active()
        self.assertEqual(result.count(), 1)

    def test_get_all(self):
        Role.objects.create(name="Inactivo", active=False)
        result = RoleRepository.get_all()
        self.assertEqual(result.count(), 2)

    def test_create(self):
        role = RoleRepository.create(name="Admin", description="Administrador")
        self.assertEqual(role.name, "Admin")
        self.assertTrue(role.active)

    def test_update(self):
        updated = RoleRepository.update(self.role, name="Profesor", active=False)
        self.assertEqual(updated.name, "Profesor")
        self.assertFalse(updated.active)

    def test_delete_soft_deletes(self):
        RoleRepository.delete(self.role)
        self.role.refresh_from_db()
        self.assertFalse(self.role.active)

    def test_add_permission(self):
        rp, created = RoleRepository.add_permission(self.role, self.permission)
        self.assertTrue(created)
        self.assertEqual(rp.role, self.role)
        self.assertEqual(rp.permission, self.permission)

    def test_add_permission_idempotent(self):
        RoleRepository.add_permission(self.role, self.permission)
        rp, created = RoleRepository.add_permission(self.role, self.permission)
        self.assertFalse(created)

    def test_remove_permission(self):
        RolePermission.objects.create(role=self.role, permission=self.permission)
        RoleRepository.remove_permission(self.role, self.permission)
        self.assertFalse(
            RolePermission.objects.filter(
                role=self.role, permission=self.permission
            ).exists()
        )


class PersonRepositoryTest(TestCase):
    """Tests para PersonRepository."""

    def setUp(self):
        doc_type, _ = self._get_or_create_doc_type()
        self.person = Person.objects.create(
            document_type=doc_type,
            document_number="1725556661",
            names="Juan",
            last_names="Pérez",
            email="juan@example.com",
        )

    def _get_or_create_doc_type(self):
        from apps.institutions.models import DocumentType

        return DocumentType.objects.get_or_create(
            code="CC", defaults={"name": "Cédula"}
        )

    def test_get_by_id_exists(self):
        result = PersonRepository.get_by_id(self.person.id)
        self.assertEqual(result, self.person)

    def test_get_by_id_not_exists(self):
        result = PersonRepository.get_by_id(99999)
        self.assertIsNone(result)

    def test_get_by_document_number_exists(self):
        result = PersonRepository.get_by_document_number("1725556661")
        self.assertEqual(result, self.person)

    def test_get_by_document_number_not_exists(self):
        result = PersonRepository.get_by_document_number("0000000000")
        self.assertIsNone(result)

    def test_get_by_email_exists(self):
        result = PersonRepository.get_by_email("juan@example.com")
        self.assertEqual(result, self.person)

    def test_get_by_email_not_exists(self):
        result = PersonRepository.get_by_email("notfound@example.com")
        self.assertIsNone(result)

    def test_get_all(self):
        result = PersonRepository.get_all()
        self.assertGreaterEqual(result.count(), 1)

    def test_search_found_by_names(self):
        result = PersonRepository.search("Juan")
        self.assertEqual(result.count(), 1)

    def test_search_found_by_last_names(self):
        result = PersonRepository.search("Pérez")
        self.assertEqual(result.count(), 1)

    def test_search_found_by_document(self):
        result = PersonRepository.search("1725556661")
        self.assertEqual(result.count(), 1)

    def test_search_not_found(self):
        result = PersonRepository.search("xyz999")
        self.assertEqual(result.count(), 0)
