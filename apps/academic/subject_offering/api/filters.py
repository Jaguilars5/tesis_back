from django_filters import rest_framework as filters

from ..infrastructure.models import SubjectOffering


class SubjectOfferingFilter(filters.FilterSet):
    section = filters.NumberFilter(field_name="section_id")
    school_year = filters.NumberFilter(field_name="section__school_year_id")
    subject_academic_config = filters.NumberFilter(
        field_name="subject_academic_config_id"
    )
    is_active = filters.BooleanFilter()

    class Meta:
        model = SubjectOffering
        fields = ["section", "school_year", "subject_academic_config", "is_active"]
