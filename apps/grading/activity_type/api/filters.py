import django_filters

from ..infrastructure.models import ActivityType


class ActivityTypeFilter(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = ActivityType
        fields = ["is_active"]
