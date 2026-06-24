from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class UserEntity:
    id: int | None
    person_id: int
    username: str
    is_active: bool
    is_staff: bool
    is_superuser: bool
    must_change_password: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class RoleEntity:
    id: int | None
    code: str | None
    name: str
    description: str
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class PermissionEntity:
    id: int | None
    code: str
    description: str
    module: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class UserRoleEntity:
    id: int | None
    user_id: int
    role_id: int
    assigned_at: datetime | None = None
    expires_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class RolePermissionEntity:
    id: int | None
    role_id: int
    permission_id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
