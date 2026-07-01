from django_filters import rest_framework as filters

from ..infrastructure.models import TeacherSubjectSection


class TeacherSubjectSectionFilter(filters.FilterSet):
    academic_grade = filters.NumberFilter(
        field_name="subject_offering__section__academic_grade_id"
    )
    school_year = filters.NumberFilter(
        field_name="subject_offering__section__school_year_id"
    )
    section = filters.NumberFilter(field_name="subject_offering__section_id")
    subject = filters.NumberFilter(
        field_name="subject_offering__subject_academic_config__subject_id"
    )
    user = filters.NumberFilter(field_name="user_id")
    is_active = filters.BooleanFilter(field_name="is_active")
    school_year_is_active = filters.BooleanFilter(
        field_name="subject_offering__section__school_year__is_active"
    )

    class Meta:
        model = TeacherSubjectSection
        fields = [
            "academic_grade",
            "school_year",
            "section",
            "subject",
            "user",
            "is_active",
            "school_year_is_active",
        ]
