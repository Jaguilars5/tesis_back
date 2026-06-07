from django_filters import (
    FilterSet,
    CharFilter,
    BooleanFilter,
)
from ...models import Student


class StudentFilter(FilterSet):
    names = CharFilter(field_name="person__names", lookup_expr="icontains")
    last_names = CharFilter(field_name="person__last_names", lookup_expr="icontains")
    document_number = CharFilter(
        field_name="person__document_number", lookup_expr="exact"
    )
    student_code = CharFilter(field_name="student_code", lookup_expr="icontains")

    class Meta:
        model = Student
        fields = ["active"]
