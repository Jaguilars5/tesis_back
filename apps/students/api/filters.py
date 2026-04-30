from django_filters import (
    FilterSet,
    CharFilter,
    ChoiceFilter,
    BooleanFilter,
    DateFromToRangeFilter,
)
from ..models import Student, Representative


class StudentFilter(FilterSet):
    """Filtros para Student"""

    names = CharFilter(field_name="names", lookup_expr="icontains")
    last_names = CharFilter(field_name="last_names", lookup_expr="icontains")
    dni = CharFilter(field_name="dni", lookup_expr="exact")
    enrollment_number = CharFilter(field_name="enrollment_number", lookup_expr="exact")
    birth_date_from = DateFromToRangeFilter(field_name="birth_date")

    class Meta:
        model = Student
        fields = ["section", "active"]


class RepresentativeFilter(FilterSet):
    """Filtros para Representative"""

    names = CharFilter(field_name="names", lookup_expr="icontains")
    last_names = CharFilter(field_name="last_names", lookup_expr="icontains")
    dni = CharFilter(field_name="dni", lookup_expr="exact")
    phone = CharFilter(field_name="phone", lookup_expr="icontains")

    class Meta:
        model = Representative
        fields = ["active"]
