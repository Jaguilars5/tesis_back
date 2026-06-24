from ..domain.entities import (
    UserEntity,
    RoleEntity,
    PermissionEntity,
    UserRoleEntity,
    RolePermissionEntity,
)
from .models import User, Role, Permission, UserRole, RolePermission


def user_to_entity(model: User) -> UserEntity:
    return UserEntity(
        id=model.id,
        person_id=model.person_id,
        username=model.username,
        is_active=model.is_active,
        is_staff=model.is_staff,
        is_superuser=model.is_superuser,
        must_change_password=model.must_change_password,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def role_to_entity(model: Role) -> RoleEntity:
    return RoleEntity(
        id=model.id,
        code=model.code,
        name=model.name,
        description=model.description,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def permission_to_entity(model: Permission) -> PermissionEntity:
    return PermissionEntity(
        id=model.id,
        code=model.code,
        description=model.description,
        module=model.module,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def user_role_to_entity(model: UserRole) -> UserRoleEntity:
    return UserRoleEntity(
        id=model.id,
        user_id=model.user_id,
        role_id=model.role_id,
        assigned_at=model.assigned_at,
        expires_at=model.expires_at,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def role_permission_to_entity(model: RolePermission) -> RolePermissionEntity:
    return RolePermissionEntity(
        id=model.id,
        role_id=model.role_id,
        permission_id=model.permission_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
