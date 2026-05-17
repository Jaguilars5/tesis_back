"""
Serializers de DRF para el módulo Grading.

Controlan la representación JSON de los modelos de calificaciones, asistencia
e incidentes de conducta.
"""

from rest_framework import serializers

from ..models import (
    Attendance,
    AttendanceStatus,
    BehaviorEvaluation,
    ClassAssignment,
    ConductIncident,
    EvaluationCriteria,
    EvaluationMacro,
    EvaluationSubcriteria,
    GradeChangeHistory,
    GradeType,
    QualitativeScale,
    StudentNote,
)


class StudentNoteSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo StudentNote.
    """

    class Meta:
        model = StudentNote
        fields = "__all__"


class AttendanceSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Attendance.
    """

    class Meta:
        model = Attendance
        fields = "__all__"


class ConductIncidentSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo ConductIncident.
    """

    class Meta:
        model = ConductIncident
        fields = "__all__"


class AttendanceStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceStatus
        fields = "__all__"


class GradeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeType
        fields = "__all__"


class QualitativeScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = QualitativeScale
        fields = "__all__"


class BehaviorEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BehaviorEvaluation
        fields = "__all__"


class EvaluationMacroSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationMacro
        fields = "__all__"


class EvaluationCriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationCriteria
        fields = "__all__"


class EvaluationSubcriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationSubcriteria
        fields = "__all__"


class ClassAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassAssignment
        fields = "__all__"


class GradeChangeHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeChangeHistory
        fields = "__all__"

