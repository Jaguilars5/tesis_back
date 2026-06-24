from django_filters import rest_framework as filters

from ..infrastructure.models import Subject


class SubjectFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains")
    code = filters.CharFilter(lookup_expr="icontains")
    is_active = filters.BooleanFilter()

    class Meta:
        model = Subject
        fields = ["name", "code", "is_active"]
