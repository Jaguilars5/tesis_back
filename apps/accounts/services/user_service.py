"""
UserService - Lógica de negocio para User.

Orquesta operaciones entre repositories, modelos y tareas asíncronas.
"""

from apps.accounts.models import Person, User, UserPermission
from apps.accounts.repositories.role_repo import RoleRepository
from apps.accounts.repositories.user_repo import UserRepository
from apps.accounts.repositories.permission_repo import PermissionRepository
from apps.institutions.models import DocumentType, Institution


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
        self, document_number, names, last_names, email, password, role_id, institution_id
    ):
        """
        Crea un nuevo usuario.

        Pasos:
        1. Validar que no exista otro usuario con el mismo email/dni
        2. Validar que el rol exista
        3. Validar que la institución exista
        4. Crear la Persona
        5. Crear el usuario asociado

        Lanza:
        - ValueError si el email ya existe
        - ValueError si el DNI ya existe
        - ValueError si el rol o institución no existe
        """
        # Verificar email único
        existing_email = self.user_repo.get_by_email(email)
        if existing_email:
            raise ValueError(f"El email {email} ya está registrado")

        # Verificar DNI único (en la institución)
        existing_dni = self.user_repo.get_by_dni(document_number, institution_id)
        if existing_dni:
            raise ValueError(f"El DNI {document_number} ya está registrado en esta institución")

        # Verificar que el rol existe
        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise ValueError(f"El rol con ID {role_id} no existe")

        # Verificar que la institución existe
        try:
            institution = Institution.objects.get(id=institution_id)
        except Institution.DoesNotExist:
            raise ValueError(f"La institución con ID {institution_id} no existe")

        # Crear la Persona
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

        # Crear el usuario
        user = self.user_repo.create(
            person=person,
            password=password,
            institution=institution,
        )
        return user

    def get_user(self, user_id):
        """Obtiene un usuario por ID."""
        return self.user_repo.get_by_id(user_id)

    def get_user_by_email(self, email):
        """Obtiene un usuario por email."""
        return self.user_repo.get_by_email(email)

    def list_users(self, institution_id=None):
        """Lista todos los usuarios activos."""
        return self.user_repo.get_all_active(institution_id)

    def list_users_by_role(self, role_id, institution_id=None):
        """Lista usuarios por rol."""
        return self.user_repo.get_by_role(role_id, institution_id)

    def update_user(self, user_id, **kwargs):
        """
        Actualiza un usuario.

        Campos soportados: names, last_names, email, role, active
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"Usuario con ID {user_id} no existe")

        # Si se actualiza email, verificar que no esté duplicado
        if "email" in kwargs and kwargs["email"] != user.email:
            existing = self.user_repo.get_by_email(kwargs["email"])
            if existing:
                raise ValueError(f"El email {kwargs['email']} ya está registrado")

        # Si se actualiza role, verificar que exista
        if "role" in kwargs:
            role = self.role_repo.get_by_id(kwargs["role"])
            if not role:
                raise ValueError(f"El rol con ID {kwargs['role']} no existe")

        return self.user_repo.update(user, **kwargs)

    def change_password(self, user_id, new_password):
        """Cambia la contraseña de un usuario."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"Usuario con ID {user_id} no existe")
        user.set_password(new_password)
        user.save()
        return user

    def deactivate_user(self, user_id):
        """Desactiva un usuario (soft-delete)."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"Usuario con ID {user_id} no existe")
        self.user_repo.delete(user)
        return user

    def grant_permission(
        self, user_id, permission_code, reason="", granted_by_id=None
    ):
        """
        Otorga un permiso específico a un usuario.

        Crea un registro en UserPermission con granted=True.
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"Usuario con ID {user_id} no existe")

        permission = self.permission_repo.get_by_code(permission_code)
        if not permission:
            raise ValueError(f"El permiso {permission_code} no existe")

        granted_by = None
        if granted_by_id:
            granted_by = self.user_repo.get_by_id(granted_by_id)

        up, created = UserPermission.objects.get_or_create(
            user=user,
            permission=permission,
            defaults={"granted": True, "reason": reason, "granted_by": granted_by},
        )

        if not created:
            up.granted = True
            up.reason = reason
            up.granted_by = granted_by
            up.save()

        return up

    def revoke_permission(
        self, user_id, permission_code, reason="", granted_by_id=None
    ):
        """
        Revoca un permiso específico a un usuario.

        Crea/actualiza un registro en UserPermission con granted=False.
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"Usuario con ID {user_id} no existe")

        permission = self.permission_repo.get_by_code(permission_code)
        if not permission:
            raise ValueError(f"El permiso {permission_code} no existe")

        granted_by = None
        if granted_by_id:
            granted_by = self.user_repo.get_by_id(granted_by_id)

        up, created = UserPermission.objects.get_or_create(
            user=user,
            permission=permission,
            defaults={"granted": False, "reason": reason, "granted_by": granted_by},
        )

        if not created:
            up.granted = False
            up.reason = reason
            up.granted_by = granted_by
            up.save()

        return up

    def has_permission(self, user_id, permission_code):
        """
        Verifica si un usuario tiene un permiso específico.
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False
        return user.has_perm(permission_code)

    def get_user_permissions(self, user_id):
        """
        Obtiene todos los permisos de un usuario (combinando rol + overrides).
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return set()
        return user.get_all_permissions()

    def search_users(self, query_string, institution_id=None):
        """
        Búsqueda de usuarios por nombre, apellido o email.
        """
        return self.user_repo.search(query_string, institution_id)
