from django_filters import rest_framework as filters

from ..infrastructure.models import ClassSchedule


class ClassScheduleFilter(filters.FilterSet):
    day_of_week = filters.NumberFilter()
    teacher_subject_section = filters.NumberFilter(
        field_name="teacher_subject_section_id"
    )
    section = filters.NumberFilter(
        field_name="teacher_subject_section__subject_offering__section_id"
    )
    teacher = filters.NumberFilter(
        field_name="teacher_subject_section__user_id"
    )
    subject_offering = filters.NumberFilter(
        field_name="teacher_subject_section__subject_offering_id"
    )
    is_active = filters.BooleanFilter()

    class Meta:
        model = ClassSchedule
        fields = [
            "day_of_week", "teacher_subject_section",
            "section", "teacher", "subject_offering", "is_active",
        ]
