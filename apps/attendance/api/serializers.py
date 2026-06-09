from rest_framework import serializers
from apps.attendance.models import (
    AbsenceType,
    Attendance,
    AttendanceStatus,
)


class AttendanceStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceStatus
        fields = "__all__"


class AbsenceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbsenceType
        fields = "__all__"


class AttendanceSerializer(serializers.ModelSerializer):
    enrollment_name = serializers.CharField(source="enrollment.__str__", read_only=True)
    teacher_subject_section_name = serializers.CharField(
        source="teacher_subject_section.__str__", read_only=True
    )
    academic_period_name = serializers.CharField(
        source="academic_period.name", read_only=True
    )
    attendance_status_name = serializers.CharField(
        source="attendance_status.name", read_only=True
    )

    class Meta:
        model = Attendance
        fields = "__all__"
        read_only_fields = ["uuid", "created_at", "updated_at", "sync_version"]
