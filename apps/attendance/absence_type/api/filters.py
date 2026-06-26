import django_filters

from ..infrastructure.models import AbsenceType


class AbsenceTypeFilter(django_filters.FilterSet):
    class Meta:
        model = AbsenceType
        fields = {
            "code": ["exact", "icontains"],
            "name": ["exact", "icontains"],
            "is_active": ["exact"],
        }
