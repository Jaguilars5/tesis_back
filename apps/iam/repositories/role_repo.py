from django.utils import timezone

from apps.iam.models import Role


class RoleRepository:
    @staticmethod
    def get_by_id(role_id):
        try:
            return Role.objects.prefetch_related("role_permissions__permission").get(
                id=role_id
            )
        except Role.DoesNotExist:
            return None

    @staticmethod
    def get_by_name(name):
        try:
            return Role.objects.prefetch_related("role_permissions__permission").get(
                name=name
            )
        except Role.DoesNotExist:
            return None

    @staticmethod
    def get_all_active():
        return (
            Role.objects.filter(is_active=True)
            .prefetch_related("role_permissions__permission")
            .order_by("name")
        )

    @staticmethod
    def get_all():
        return Role.objects.prefetch_related("role_permissions__permission").order_by(
            "name"
        )

    @staticmethod
    def create(name, description="", active=True):
        now = timezone.now()
        role = Role(
            name=name, description=description, is_active=active,
            created_at=now, updated_at=now,
        )
        role.save()
        return role

    @staticmethod
    def update(role, **kwargs):
        allowed_fields = {"name", "description", "is_active"}
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(role, key, value)
        role.updated_at = timezone.now()
        role.save()
        return role

    @staticmethod
    def delete(role):
        role.is_active = False
        role.save()

    @staticmethod
    def get_permissions(role_id):
        from apps.iam.models import Permission

        return Permission.objects.filter(permission_roles__role_id=role_id).distinct()

    @staticmethod
    def add_permission(role, permission):
        from apps.iam.models import RolePermission

        rp, created = RolePermission.objects.get_or_create(
            role=role, permission=permission
        )
        return rp, created

    @staticmethod
    def remove_permission(role, permission):
        from apps.iam.models import RolePermission

        return RolePermission.objects.filter(role=role, permission=permission).delete()

    @staticmethod
    def set_permissions(role, permission_objects):
        from apps.iam.models import RolePermission

        RolePermission.objects.filter(role_id=role.id).delete()
        rps = [RolePermission(role=role, permission=p) for p in permission_objects]
        return RolePermission.objects.bulk_create(rps)
