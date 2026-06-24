import django_filters

from ..infrastructure.models import AttendanceStatus


class AttendanceStatusFilter(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = AttendanceStatus
        fields = ["is_active"]
