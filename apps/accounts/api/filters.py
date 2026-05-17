"""
Filtros para los endpoints de API del módulo accounts.

Utiliza django-filter para permitir filtrado en los listados.
"""

import django_filters
from apps.accounts.models import User, Role, Permission


class PermissionFilter(django_filters.FilterSet):
    """Filtros para Permission."""

    module = django_filters.CharFilter(field_name="module", lookup_expr="iexact")

    class Meta:
        model = Permission
        fields = ["module"]


class RoleFilter(django_filters.FilterSet):
    """Filtros para Role."""

    active = django_filters.BooleanFilter(field_name="active")

    class Meta:
        model = Role
        fields = ["active"]


class UserFilter(django_filters.FilterSet):
    """Filtros para User."""

    active = django_filters.BooleanFilter(field_name="active")
    institution_id = django_filters.NumberFilter(field_name="institution_id")
    role_id = django_filters.NumberFilter(field_name="user_roles__role_id")
    dni = django_filters.CharFilter(field_name="person__document_number", lookup_expr="iexact")

    class Meta:
        model = User
        fields = ["active", "institution_id", "role_id", "dni"]
