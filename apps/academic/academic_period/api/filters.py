from django_filters import rest_framework as filters
from ..infrastructure.models import AcademicPeriod


class AcademicPeriodFilter(filters.FilterSet):
    school_year = filters.NumberFilter(field_name="school_year_id")
    period_type = filters.NumberFilter(field_name="period_type_id")
    is_active = filters.BooleanFilter()
    is_regular_period = filters.BooleanFilter()
    start_date_from = filters.DateFilter(field_name="start_date", lookup_expr="gte")
    start_date_to = filters.DateFilter(field_name="start_date", lookup_expr="lte")

    class Meta:
        model = AcademicPeriod
        fields = ["school_year", "period_type", "is_active", "is_regular_period"]
