from django_filters import rest_framework as filters

from ..infrastructure.models import PeriodType


class PeriodTypeFilter(filters.FilterSet):
    code = filters.CharFilter(lookup_expr="icontains")
    name = filters.CharFilter(lookup_expr="icontains")
    is_active = filters.BooleanFilter()

    class Meta:
        model = PeriodType
        fields = ["code", "name", "divisions_per_year", "is_active"]
