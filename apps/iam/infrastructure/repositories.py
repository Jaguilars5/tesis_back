from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.core.repositories.base import BaseRepository

from ..domain.repositories.interfaces import (
    UserRepositoryInterface,
    RoleRepositoryInterface,
    PermissionRepositoryInterface,
)
from .models import User, Role, Permission, UserRole, RolePermission


class UserRepository(BaseRepository, UserRepositoryInterface):
    model = User

    @classmethod
    def get_by_username(cls, username):
        try:
            return cls.model.objects.get(username=username)
        except cls.model.DoesNotExist:
            return None

    @classmethod
    def get_by_username_or_email(cls, identifier):
        return cls.model.objects.filter(
            Q(username__iexact=identifier) | Q(person__email__iexact=identifier),
            is_active=True,
        ).first()

    @classmethod
    def get_by_email(cls, email):
        try:
            return cls.model.objects.get(person__email=email)
        except cls.model.DoesNotExist:
            return None

    @classmethod
    def get_by_dni(cls, dni):
        try:
            return cls.model.objects.get(person__document_number=dni)
        except cls.model.DoesNotExist:
            return None

    @classmethod
    def get_all_active(cls):
        return cls.model.objects.filter(is_active=True).order_by("username")

    @classmethod
    def get_by_role(cls, role_id):
        return cls.model.objects.filter(
            user_roles__role_id=role_id, is_active=True
        ).distinct().order_by("username")

    @classmethod
    def get_by_role_code(cls, code):
        return cls.model.objects.filter(
            user_roles__role__code=code, is_active=True
        ).distinct().order_by("username")

    @classmethod
    def create_user(cls, person, password, is_superuser=False, **extra_fields):
        return User.objects.create_user(
            person=person,
            password=password,
            is_superuser=is_superuser,
            **extra_fields,
        )

    @classmethod
    def update_user(cls, user, **kwargs):
        allowed_fields = {"username", "is_active"}
        email_value = kwargs.pop("email", None)
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(user, key, value)
        user.save()
        if email_value is not None and user.person:
            user.person.email = email_value
            user.person.save(update_fields=["email", "updated_at"])
        return user

    @classmethod
    def delete_user(cls, user):
        user.is_active = False
        user.save()

    @classmethod
    def change_password(cls, user, new_password):
        user.set_password(new_password)
        user.must_change_password = False
        user.save(update_fields=["password", "must_change_password", "updated_at"])
        return user

    @classmethod
    def add_user_role(cls, user, role):
        return UserRole.objects.create(user=user, role=role)

    @classmethod
    @transaction.atomic
    def create_user_with_person(cls, document_number, names, last_names, email, password, role_id,
                                 birth_date=None, phone="", document_type_id=None, parish_id=None):
        from datetime import date
        from apps.people.models import DocumentType, Person

        if not document_type_id:
            doc_type = DocumentType.objects.get_or_create(
                code="CC", defaults={"name": "Cédula de Ciudadanía"}
            )[0]
        else:
            doc_type = DocumentType.objects.get(id=document_type_id)

        person = Person.objects.create(
            document_type=doc_type,
            document_number=document_number,
            names=names,
            last_names=last_names,
            email=email,
            phone=phone,
            birth_date=birth_date or date(2000, 1, 1),
            parish_id=parish_id,
        )
        user = cls.model.objects.create_user(person=person, password=password)
        role = Role.objects.get(id=role_id)
        UserRole.objects.create(user=user, role=role)
        return user

    @classmethod
    def bulk_create(cls, user_list):
        now = timezone.now()
        users = []
        for user_data in user_list:
            user = User(
                person=user_data["person"],
                created_at=now,
                updated_at=now,
            )
            user.set_password(user_data["password"])
            users.append(user)
        return User.objects.bulk_create(users)

    @classmethod
    def search_by_role_code(cls, role_code, search=None):
        qs = cls.model.objects.filter(
            user_roles__role__code=role_code, is_active=True
        ).distinct().order_by("username")
        if search:
            qs = qs.filter(
                Q(person__names__icontains=search) |
                Q(person__last_names__icontains=search) |
                Q(person__document_number__icontains=search)
            )
        return qs

    @classmethod
    def search(cls, query_string):
        return cls.model.objects.filter(
            Q(person__names__icontains=query_string)
            | Q(person__last_names__icontains=query_string)
            | Q(username__icontains=query_string)
            | Q(person__email__icontains=query_string),
            is_active=True,
        ).order_by("username")


class RoleRepository(BaseRepository, RoleRepositoryInterface):
    model = Role

    @classmethod
    def get_by_name(cls, name):
        try:
            return cls.model.objects.prefetch_related("role_permissions__permission").get(name=name)
        except cls.model.DoesNotExist:
            return None

    @classmethod
    def get_all_active(cls):
        return cls.model.objects.filter(is_active=True).prefetch_related("role_permissions__permission").order_by("name")

    @classmethod
    def get_all(cls):
        return cls.model.objects.prefetch_related("role_permissions__permission").order_by("name")

    @classmethod
    def create_role(cls, name, description="", active=True):
        now = timezone.now()
        role = cls.model(name=name, description=description, is_active=active, created_at=now, updated_at=now)
        role.save()
        return role

    @classmethod
    def update_role(cls, role, **kwargs):
        allowed_fields = {"name", "description", "is_active"}
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(role, key, value)
        role.save()
        return role

    @classmethod
    def delete_role(cls, role):
        role.is_active = False
        role.save()

    @classmethod
    def get_permissions(cls, role_id):
        return Permission.objects.filter(permission_roles__role_id=role_id).distinct()

    @classmethod
    def add_permission(cls, role, permission):
        rp, created = RolePermission.objects.get_or_create(role=role, permission=permission)
        return rp, created

    @classmethod
    def remove_permission(cls, role, permission):
        return RolePermission.objects.filter(role=role, permission=permission).delete()

    @classmethod
    def get_cascade_counts(cls, instance_id: int) -> dict[str, int]:
        count = cls.model.objects.filter(pk=instance_id).count()
        users = User.objects.filter(user_roles__role_id=instance_id, is_active=True).count()
        counts = {}
        if users:
            counts["usuarios"] = users
        return counts

    @classmethod
    @transaction.atomic
    def deactivate_cascade(cls, instance_id: int) -> int:
        total = 0
        affected = UserRole.objects.filter(role_id=instance_id).select_related("user")
        for ur in affected:
            if ur.user.is_active:
                ur.user.is_active = False
                ur.user.save(update_fields=["is_active"])
                total += 1
        cls.model.objects.filter(pk=instance_id).update(is_active=False)
        return total

    @classmethod
    def set_permissions(cls, role, permission_objects):
        RolePermission.objects.filter(role_id=role.id).delete()
        rps = [RolePermission(role=role, permission=p) for p in permission_objects]
        return RolePermission.objects.bulk_create(rps)


class PermissionRepository(BaseRepository, PermissionRepositoryInterface):
    model = Permission

    @classmethod
    def get_by_code(cls, code):
        try:
            return cls.model.objects.get(code=code)
        except cls.model.DoesNotExist:
            return None

    @classmethod
    def get_by_module(cls, module):
        return cls.model.objects.filter(module=module).order_by("code")

    @classmethod
    def create_permission(cls, code, description="", module=""):
        now = timezone.now()
        perm = cls.model(code=code, description=description, module=module, created_at=now, updated_at=now)
        perm.save()
        return perm

    @classmethod
    def create_many(cls, permission_list):
        now = timezone.now()
        permissions = [
            cls.model(
                code=p["code"],
                description=p.get("description", ""),
                module=p.get("module", ""),
                created_at=now,
                updated_at=now,
            )
            for p in permission_list
        ]
        return cls.model.objects.bulk_create(permissions, ignore_conflicts=True)

    @classmethod
    def update_permission(cls, permission, **kwargs):
        allowed_fields = {"description", "module"}
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(permission, key, value)
        permission.save()
        return permission

    @classmethod
    def delete_permission(cls, permission):
        permission.delete()

    @classmethod
    def count_role_permissions(cls, permission_id):
        return RolePermission.objects.filter(permission_id=permission_id).count()

    @classmethod
    def search(cls, query_string):
        return cls.model.objects.filter(
            Q(code__icontains=query_string) | Q(description__icontains=query_string)
        ).order_by("code")
