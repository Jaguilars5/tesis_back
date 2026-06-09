from apps.iam.repositories.permission_repo import PermissionRepository


class PermissionService:
    def __init__(self):
        self.permission_repo = PermissionRepository()

    def create_permission(self, code, description="", module=""):
        existing = self.permission_repo.get_by_code(code)
        if existing:
            raise ValueError(f"El permiso '{code}' ya existe")

        return self.permission_repo.create(code, description, module)

    def create_permissions_bulk(self, permission_list):
        return self.permission_repo.create_many(permission_list)

    def get_permission(self, permission_id):
        return self.permission_repo.get_by_id(permission_id)

    def get_permission_by_code(self, code):
        return self.permission_repo.get_by_code(code)

    def list_permissions(self):
        return self.permission_repo.get_all()

    def list_permissions_by_module(self, module):
        return self.permission_repo.get_by_module(module)

    def update_permission(self, permission_id, **kwargs):
        permission = self.permission_repo.get_by_id(permission_id)
        if not permission:
            raise ValueError(f"Permiso con ID {permission_id} no existe")

        return self.permission_repo.update(permission, **kwargs)

    def delete_permission(self, permission_id):
        permission = self.permission_repo.get_by_id(permission_id)
        if not permission:
            raise ValueError(f"Permiso con ID {permission_id} no existe")

        role_count = self.permission_repo.count_role_permissions(permission_id)
        if role_count > 0:
            raise ValueError(
                f"No se puede eliminar el permiso '{permission.code}' porque está asignado a {role_count} rol(es)"
            )

        self.permission_repo.delete(permission)
        return True

    def search_permissions(self, query_string):
        return self.permission_repo.search(query_string)

    def get_permissions_for_module(self, module_name):
        return self.permission_repo.get_by_module(module_name)
