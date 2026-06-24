import django_filters

from ..infrastructure.models import Section


class SectionFilter(django_filters.FilterSet):
    class Meta:
        model = Section
        fields = {
            "parallel": ["exact", "icontains"],
            "academic_grade": ["exact"],
            "school_year": ["exact"],
            "is_active": ["exact"],
        }
