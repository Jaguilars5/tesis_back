"""
Serializers de DRF para el módulo Grading.

Controlan la representación JSON de los modelos de calificaciones y evaluaciones.
"""

from rest_framework import serializers

from ..models import (
    ActivityType,
    BlockComponent,
    ComponentIndicator,
    EvaluationBlock,
    EvaluationType,
    EvaluativeActivity,
    GradeChangeHistory,
    GradeType,
    LearningReport,
    PeriodGradeSummary,
    ProjectNote,
    PromotionStatus,
    QualitativeScale,
    RecoveryProcess,
    RecoveryProcessType,
    RecoverySession,
    StudentNote,
)
from ..models.qualitative_scale_sublevel import QualitativeScaleSublevel


class StudentNoteSerializer(serializers.ModelSerializer):
    enrollment_name = serializers.CharField(source="enrollment.__str__", read_only=True)
    evaluative_activity_title = serializers.CharField(
        source="evaluative_activity.title", read_only=True
    )
    grade_type_name = serializers.CharField(source="grade_type.name", read_only=True)
    qualitative_scale_name = serializers.CharField(
        source="qualitative_scale.name", read_only=True
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
                    "El subnivel del estudiante usa calificación cualitativa. "
                    "No se permiten calificaciones numéricas."
                )
            if not has_qualitative and grading_mode == "QUALITATIVE":
                raise serializers.ValidationError(
                    "El subnivel del estudiante usa calificación numérica. "
                    "No se permiten calificaciones cualitativas."
                )
        return super().validate(attrs)

    class Meta:
        model = StudentNote
        fields = "__all__"


class EvaluationBlockSerializer(serializers.ModelSerializer):
    academic_period_name = serializers.CharField(
        source="academic_period.name", read_only=True
    )

    class Meta:
        model = EvaluationBlock
        fields = "__all__"


class BlockComponentSerializer(serializers.ModelSerializer):
    evaluation_block_name = serializers.CharField(
        source="evaluation_block.name", read_only=True
    )

    class Meta:
        model = BlockComponent
        fields = "__all__"


class ComponentIndicatorSerializer(serializers.ModelSerializer):
    block_component_name = serializers.CharField(
        source="block_component.name", read_only=True
    )

    class Meta:
        model = ComponentIndicator
        fields = "__all__"


class EvaluativeActivitySerializer(serializers.ModelSerializer):
    component_indicator_name = serializers.CharField(
        source="component_indicator.name", read_only=True
    )
    teacher_subject_section_name = serializers.CharField(
        source="teacher_subject_section.__str__", read_only=True
    )

    class Meta:
        model = EvaluativeActivity
        fields = "__all__"


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
        source="qualitative_scale.name", read_only=True
    )

    class Meta:
        model = PeriodGradeSummary
        fields = "__all__"


class RecoveryProcessSerializer(serializers.ModelSerializer):
    period_grade_summary_name = serializers.CharField(
        source="period_grade_summary.__str__", read_only=True
    )
    managed_by_user_name = serializers.CharField(
        source="managed_by_user.person.get_full_name", read_only=True
    )

    class Meta:
        model = RecoveryProcess
        fields = "__all__"


class ProjectNoteSerializer(serializers.ModelSerializer):
    enrollment_name = serializers.CharField(source="enrollment.__str__", read_only=True)
    interdisciplinary_project_title = serializers.CharField(
        source="interdisciplinary_project.title", read_only=True
    )

    class Meta:
        model = ProjectNote
        fields = "__all__"


class GradeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeType
        fields = "__all__"


class QualitativeScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = QualitativeScale
        fields = "__all__"


class EvaluationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationType
        fields = "__all__"


class ActivityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityType
        fields = "__all__"


class PromotionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromotionStatus
        fields = "__all__"


class RecoveryProcessTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecoveryProcessType
        fields = "__all__"


class LearningReportSerializer(serializers.ModelSerializer):
    enrollment_name = serializers.CharField(source="enrollment.__str__", read_only=True)
    academic_period_name = serializers.CharField(
        source="academic_period.name", read_only=True
    )
    created_by_name = serializers.CharField(
        source="created_by.person.get_full_name", read_only=True
    )
    evaluated_by_name = serializers.CharField(
        source="evaluated_by.person.get_full_name", read_only=True
    )

    class Meta:
        model = LearningReport
        fields = "__all__"


class RecoverySessionSerializer(serializers.ModelSerializer):
    recovery_process_name = serializers.CharField(
        source="recovery_process.__str__", read_only=True
    )

    class Meta:
        model = RecoverySession
        fields = "__all__"
