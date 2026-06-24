from django_filters import rest_framework as filters

from ..infrastructure.models import AcademicGrade


class AcademicGradeFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains")
    academic_sublevel = filters.NumberFilter(field_name="academic_sublevel_id")
    is_active = filters.BooleanFilter()

    class Meta:
        model = AcademicGrade
        fields = ["name", "academic_sublevel", "is_active"]
