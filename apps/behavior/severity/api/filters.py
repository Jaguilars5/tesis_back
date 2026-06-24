import django_filters

from ..infrastructure.models import Severity


class SeverityFilter(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = Severity
        fields = ["is_active"]
