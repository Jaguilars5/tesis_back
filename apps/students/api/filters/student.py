from django_filters import (
    FilterSet,
    CharFilter,
    BooleanFilter,
    NumberFilter,
)

from django.db.models import Q

from ...infrastructure.models import Student


class StudentFilter(FilterSet):
    names = CharFilter(field_name="user__person__names", lookup_expr="icontains")
    last_names = CharFilter(field_name="user__person__last_names", lookup_expr="icontains")
    document_number = CharFilter(
        field_name="user__person__document_number", lookup_expr="exact"
    )
    student_code = CharFilter(field_name="student_code", lookup_expr="icontains")
    city = NumberFilter(field_name="user__person__parish__city")
    parish = NumberFilter(field_name="user__person__parish")
    has_special_needs = BooleanFilter()
    current_academic_year = BooleanFilter(method="filter_current_academic_year")

    class Meta:
        model = Student
        fields = ["is_active"]

    def filter_current_academic_year(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(enrollments__section__school_year__is_active=True)
                & Q(enrollments__enrollment_status="ACT")
            ).distinct()
        return queryset
