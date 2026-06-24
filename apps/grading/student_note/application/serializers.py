from rest_framework import serializers

from ..infrastructure.models import (
    StudentNote,
    GradeChangeHistory,
    PeriodGradeSummary,
)
from apps.grading.qualitative_scale.infrastructure.models import QualitativeScaleSublevel


class StudentNoteSerializer(serializers.ModelSerializer):
    enrollment_name = serializers.CharField(source="enrollment.__str__", read_only=True)
    evaluative_activity_title = serializers.CharField(
        source="evaluative_activity.title", read_only=True
    )
    qualitative_scale_name = serializers.CharField(
        source="qualitative_scale.name", read_only=True, allow_null=True
    )

    def validate(self, attrs):
        grading_mode = attrs.get("grading_mode")
        enrollment = attrs.get("enrollment")
        if grading_mode and enrollment:
            sublevel = enrollment.section.academic_grade.academic_sublevel
            has_qualitative = QualitativeScaleSublevel.objects.filter(
                sublevel=sublevel, is_active=True
            ).exists()
            if has_qualitative and grading_mode == "NUMERIC":
                raise serializers.ValidationError(
                    "El subnivel del estudiante usa calificaci\u00f3n cualitativa. "
                    "No se permiten calificaciones num\u00e9ricas."
                )
            if not has_qualitative and grading_mode == "QUALITATIVE":
                raise serializers.ValidationError(
                    "El subnivel del estudiante usa calificaci\u00f3n num\u00e9rica. "
                    "No se permiten calificaciones cualitativas."
                )
        return super().validate(attrs)

    class Meta:
        model = StudentNote
        fields = "__all__"
        read_only_fields = ["uuid", "created_at", "updated_at", "sync_version", "sync_status", "synced_at"]


class GradeChangeHistorySerializer(serializers.ModelSerializer):
    student_note_name = serializers.CharField(
        source="student_note.__str__", read_only=True
    )
    modified_by_user_name = serializers.CharField(
        source="modified_by_user.person.get_full_name", read_only=True
    )

    class Meta:
        model = GradeChangeHistory
        fields = "__all__"


class PeriodGradeSummarySerializer(serializers.ModelSerializer):
    enrollment_name = serializers.CharField(source="enrollment.__str__", read_only=True)
    subject_offering_name = serializers.CharField(
        source="subject_offering.__str__", read_only=True
    )
    academic_period_name = serializers.CharField(
        source="academic_period.name", read_only=True
    )
    qualitative_scale_name = serializers.CharField(
        source="qualitative_scale.name", read_only=True, allow_null=True
    )

    class Meta:
        model = PeriodGradeSummary
        fields = "__all__"
