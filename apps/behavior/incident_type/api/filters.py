import django_filters

from ..infrastructure.models import IncidentType


class IncidentTypeFilter(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = IncidentType
        fields = ["is_active"]
