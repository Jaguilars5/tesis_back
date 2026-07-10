from rest_framework import serializers

from ..infrastructure.models import (
    StudentNote,
    GradeChangeHistory,
    PeriodGradeSummary,
    AnnualGradeSummary,
)


class StudentNoteSerializer(serializers.ModelSerializer):
    enrollment_name = serializers.CharField(read_only=True)
    evaluative_activity_title = serializers.CharField(read_only=True)
    qualitative_scale_name = serializers.CharField(read_only=True, allow_null=True)
    # Metadata de la actividad evaluativa relacionada. Permite que las vistas
    # de calificaciones del estudiante (scoped por matricula) sean autosuficientes
    # sin tener que cruzar contra el endpoint global de actividades evaluativas.
    subject_offering = serializers.SerializerMethodField()
    subject_offering_name = serializers.SerializerMethodField()
    activity_type = serializers.SerializerMethodField()
    activity_type_name = serializers.SerializerMethodField()
    max_score = serializers.SerializerMethodField()
    academic_period = serializers.SerializerMethodField()
    academic_period_name = serializers.SerializerMethodField()

    class Meta:
        model = StudentNote
        fields = "__all__"
        read_only_fields = ["uuid", "created_at", "updated_at", "sync_version", "sync_status", "synced_at"]

    def get_subject_offering(self, obj):
        act = obj.evaluative_activity
        tss = act.teacher_subject_section if act else None
        return tss.subject_offering_id if tss else None

    def get_subject_offering_name(self, obj):
        return obj.evaluative_activity.subject_offering_name if obj.evaluative_activity else None

    def get_activity_type(self, obj):
        return obj.evaluative_activity.activity_type_id if obj.evaluative_activity else None

    def get_activity_type_name(self, obj):
        return obj.evaluative_activity.activity_type_name if obj.evaluative_activity else None

    def get_max_score(self, obj):
        return str(obj.evaluative_activity.max_score) if obj.evaluative_activity else None

    def _evaluation_block(self, obj):
        act = obj.evaluative_activity
        comp = act.block_component if act else None
        return comp.evaluation_block if comp else None

    def get_academic_period(self, obj):
        block = self._evaluation_block(obj)
        return block.academic_period_id if block else None

    def get_academic_period_name(self, obj):
        block = self._evaluation_block(obj)
        return block.academic_period_name if block else None


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


class AnnualGradeSummarySerializer(serializers.ModelSerializer):
    enrollment_name = serializers.CharField(read_only=True)
    subject_offering_name = serializers.CharField(read_only=True)
    school_year_name = serializers.CharField(read_only=True)

    class Meta:
        model = AnnualGradeSummary
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]
