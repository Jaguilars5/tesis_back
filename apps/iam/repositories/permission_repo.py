from django.utils import timezone

from apps.iam.models import Permission


class PermissionRepository:
    @staticmethod
    def get_by_id(permission_id):
        try:
            return Permission.objects.get(id=permission_id)
        except Permission.DoesNotExist:
            return None

    @staticmethod
    def get_by_code(code):
        try:
            return Permission.objects.get(code=code)
        except Permission.DoesNotExist:
            return None

    @staticmethod
    def get_all():
        return Permission.objects.order_by("code")

    @staticmethod
    def get_by_module(module):
        return Permission.objects.filter(module=module).order_by("code")

    @staticmethod
    def create(code, description="", module=""):
        now = timezone.now()
        permission = Permission(
            code=code, description=description, module=module,
            created_at=now, updated_at=now,
        )
        permission.save()
        return permission

    @staticmethod
    def create_many(permission_list):
        now = timezone.now()
        permissions = [
            Permission(
                code=p["code"],
                description=p.get("description", ""),
                module=p.get("module", ""),
                created_at=now,
                updated_at=now,
            )
            for p in permission_list
        ]
        return Permission.objects.bulk_create(permissions, ignore_conflicts=True)

    @staticmethod
    def update(permission, **kwargs):
        allowed_fields = {"description", "module"}
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(permission, key, value)
        permission.updated_at = timezone.now()
        permission.save()
        return permission

    @staticmethod
    def delete(permission):
        permission.delete()

    @staticmethod
    def count_role_permissions(permission_id):
        from apps.iam.models import RolePermission

        return RolePermission.objects.filter(permission_id=permission_id).count()

    @staticmethod
    def search(query_string):
        from django.db.models import Q

        return Permission.objects.filter(
            Q(code__icontains=query_string) | Q(description__icontains=query_string)
        ).order_by("code")
