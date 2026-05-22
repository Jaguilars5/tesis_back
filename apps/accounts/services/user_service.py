"""
UserService - Lógica de negocio para User.

Orquesta operaciones entre repositories, modelos y tareas asíncronas.
"""

from apps.accounts.models import Person, User
from apps.accounts.repositories.role_repo import RoleRepository
from apps.accounts.repositories.user_repo import UserRepository
from apps.accounts.repositories.permission_repo import PermissionRepository
from apps.institutions.models import DocumentType


class UserService:
    """
    Servicio de lógica de negocio para User.

    Nunca accede directamente a User.objects — siempre usa UserRepository.
    """

    def __init__(self):
        self.user_repo = UserRepository()
        self.role_repo = RoleRepository()
        self.permission_repo = PermissionRepository()

    def create_user(
        self, document_number, names, last_names, email, password, role_id
    ):
        existing_email = self.user_repo.get_by_email(email)
        if existing_email:
            raise ValueError(f"El email {email} ya está registrado")

        existing_dni = self.user_repo.get_by_dni(document_number)
        if existing_dni:
            raise ValueError(f"El DNI {document_number} ya está registrado")

        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise ValueError(f"El rol con ID {role_id} no existe")

        doc_type = DocumentType.objects.get_or_create(
            code="CC", defaults={"name": "Cédula de Ciudadanía"}
        )[0]
        person = Person.objects.create(
            document_type=doc_type,
            document_number=document_number,
            names=names,
            last_names=last_names,
            email=email,
        )

        user = self.user_repo.create(
            person=person,
            password=password,
        )
        return user

    def get_user(self, user_id):
        return self.user_repo.get_by_id(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_by_email(email)

    def list_users(self):
        return self.user_repo.get_all_active()

    def list_users_by_role(self, role_id):
        return self.user_repo.get_by_role(role_id)

    def update_user(self, user_id, **kwargs):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"Usuario con ID {user_id} no existe")
        if "email" in kwargs and kwargs["email"] != user.email:
            existing = self.user_repo.get_by_email(kwargs["email"])
            if existing:
                raise ValueError(f"El email {kwargs['email']} ya está registrado")
        if "role" in kwargs:
            role = self.role_repo.get_by_id(kwargs["role"])
            if not role:
                raise ValueError(f"El rol con ID {kwargs['role']} no existe")
        return self.user_repo.update(user, **kwargs)

    def change_password(self, user_id, new_password):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"Usuario con ID {user_id} no existe")
        user.set_password(new_password)
        user.save()
        return user

    def deactivate_user(self, user_id):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"Usuario con ID {user_id} no existe")
        self.user_repo.delete(user)
        return user

    def has_permission(self, user_id, permission_code):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False
        return user.has_perm(permission_code)

    def get_user_permissions(self, user_id):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return set()
        return user.get_all_permissions()

    def search_users(self, query_string):
        return self.user_repo.search(query_string)
