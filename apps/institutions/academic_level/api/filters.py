import django_filters

from ..infrastructure.models import AcademicLevel


class AcademicLevelFilter(django_filters.FilterSet):
    class Meta:
        model = AcademicLevel
        fields = {
            "name": ["exact", "icontains"],
            "is_active": ["exact"],
        }
