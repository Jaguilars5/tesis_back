import django_filters

from ..infrastructure.models import SchoolYear


class SchoolYearFilter(django_filters.FilterSet):
    class Meta:
        model = SchoolYear
        fields = {
            "start_date": ["exact", "gte", "lte"],
            "end_date": ["exact", "gte", "lte"],
            "is_active": ["exact"],
        }
