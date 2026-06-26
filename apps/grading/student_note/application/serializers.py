from rest_framework import serializers

from ..infrastructure.models import (
    StudentNote,
    GradeChangeHistory,
    PeriodGradeSummary,
)


class StudentNoteSerializer(serializers.ModelSerializer):
    enrollment_name = serializers.CharField(read_only=True)
    evaluative_activity_title = serializers.CharField(read_only=True)
    qualitative_scale_name = serializers.CharField(read_only=True, allow_null=True)

    class Meta:
        model = StudentNote
        fields = "__all__"
        read_only_fields = ["uuid", "created_at", "updated_at", "sync_version", "sync_status", "synced_at"]


class GradeChangeHistorySerializer(serializers.ModelSerializer):
    student_note_name = serializers.CharField(read_only=True)
    modified_by_user_name = serializers.CharField(read_only=True)

    class Meta:
        model = GradeChangeHistory
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class PeriodGradeSummarySerializer(serializers.ModelSerializer):
    enrollment_name = serializers.CharField(read_only=True)
    subject_offering_name = serializers.CharField(read_only=True)
    academic_period_name = serializers.CharField(read_only=True)
    qualitative_scale_name = serializers.CharField(read_only=True, allow_null=True)

    class Meta:
        model = PeriodGradeSummary
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]
