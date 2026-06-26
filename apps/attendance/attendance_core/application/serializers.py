from rest_framework import serializers

from ..infrastructure.models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    absence_type_name = serializers.CharField(read_only=True)
    attendance_status_name = serializers.CharField(read_only=True)
    academic_period_name = serializers.CharField(read_only=True)
    enrollment_name = serializers.CharField(read_only=True)
    teacher_subject_section_name = serializers.CharField(read_only=True)
    class_schedule_name = serializers.CharField(read_only=True)

    class Meta:
        model = Attendance
        fields = [
            "id",
            "absence_type",
            "attendance_status",
            "academic_period",
            "enrollment",
            "teacher_subject_section",
            "class_schedule",
            "attendance_date",
            "observation",
            "uuid",
            "sync_status",
            "sync_version",
            "synced_at",
            "device_origin",
            "conflict_resolved",
            "conflict_notes",
            "created_at",
            "updated_at",
            "absence_type_name",
            "attendance_status_name",
            "academic_period_name",
            "enrollment_name",
            "teacher_subject_section_name",
            "class_schedule_name",
        ]
        read_only_fields = [
            "uuid", "created_at", "updated_at", "sync_version",
            "sync_status", "synced_at", "device_origin",
            "conflict_resolved", "conflict_notes",
        ]
