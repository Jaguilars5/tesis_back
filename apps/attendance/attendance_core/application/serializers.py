from rest_framework import serializers

from ..infrastructure.models import Attendance


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
    class_schedule_name = serializers.SerializerMethodField(read_only=True)

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
            "enrollment_name",
            "teacher_subject_section_name",
            "academic_period_name",
            "attendance_status_name",
            "class_schedule_name",
        ]
        read_only_fields = [
            "uuid", "created_at", "updated_at", "sync_version",
        ]

    def get_class_schedule_name(self, obj):
        if obj.class_schedule_id and obj.class_schedule:
            return str(obj.class_schedule)
        return None
