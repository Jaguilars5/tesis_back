import django_filters

from ..infrastructure.models import Attendance


class AttendanceFilter(django_filters.FilterSet):
    enrollment = django_filters.NumberFilter(field_name="enrollment_id")
    teacher_subject_section = django_filters.NumberFilter(field_name="teacher_subject_section_id")
    attendance_date = django_filters.DateFilter(field_name="attendance_date")
    attendance_date_after = django_filters.DateFilter(field_name="attendance_date", lookup_expr="gte")
    attendance_date_before = django_filters.DateFilter(field_name="attendance_date", lookup_expr="lte")
    academic_period = django_filters.NumberFilter(field_name="academic_period_id")
    attendance_status = django_filters.NumberFilter(field_name="attendance_status_id")
    absence_type = django_filters.NumberFilter(field_name="absence_type_id")
    day_of_week = django_filters.NumberFilter(method="filter_day_of_week")

    def filter_day_of_week(self, queryset, name, value):
        django_day = (value % 7) + 1
        return queryset.filter(attendance_date__week_day=django_day)

    class Meta:
        model = Attendance
        fields = [
            "enrollment",
            "teacher_subject_section",
            "attendance_date",
            "attendance_date_after",
            "attendance_date_before",
            "academic_period",
            "attendance_status",
            "absence_type",
            "day_of_week",
        ]
