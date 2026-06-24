import django_filters

from ..infrastructure.models import AbsenceType


class AbsenceTypeFilter(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = AbsenceType
        fields = ["is_active"]
