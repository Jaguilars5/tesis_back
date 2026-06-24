import django_filters

from ..infrastructure.models import AcademicSublevel


class AcademicSublevelFilter(django_filters.FilterSet):
    class Meta:
        model = AcademicSublevel
        fields = {
            "name": ["exact", "icontains"],
            "code": ["exact", "icontains"],
            "academic_level": ["exact"],
            "is_active": ["exact"],
        }
