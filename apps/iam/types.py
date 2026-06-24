from typing import TypedDict


class CreateUserPayload(TypedDict, total=False):
    document_number: str
    names: str
    last_names: str
    email: str
    password: str
    role_id: int


class CreateRolePayload(TypedDict, total=False):
    name: str
    description: str
    is_active: bool


class CreatePermissionPayload(TypedDict, total=False):
    code: str
    description: str
    module: str


class AssignPermissionsPayload(TypedDict, total=False):
    permission_codes: list[str]
