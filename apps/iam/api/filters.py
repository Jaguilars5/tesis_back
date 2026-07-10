import django_filters
from ..infrastructure.models import User, Role, Permission


class PermissionFilter(django_filters.FilterSet):
    module = django_filters.CharFilter(field_name="module", lookup_expr="iexact")

    class Meta:
        model = Permission
        fields = ["module"]


class RoleFilter(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = Role
        fields = ["is_active"]


class UserFilter(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter(field_name="is_active")
    role_id = django_filters.NumberFilter(field_name="user_roles__role_id")
    dni = django_filters.CharFilter(field_name="person__document_number", lookup_expr="iexact")

    class Meta:
        model = User
        fields = ["is_active", "role_id", "dni"]
