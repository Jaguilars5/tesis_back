from django_filters import rest_framework as filters

from ..infrastructure.models import SubjectAcademicConfig


class SubjectAcademicConfigFilter(filters.FilterSet):
    subject = filters.NumberFilter(field_name="subject_id")
    academic_grade = filters.NumberFilter(field_name="academic_grade_id")
    is_required = filters.BooleanFilter()
    is_active = filters.BooleanFilter()

    class Meta:
        model = SubjectAcademicConfig
        fields = ["subject", "academic_grade", "is_required", "is_active"]
