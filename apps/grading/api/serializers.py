"""
Serializers de DRF para el módulo Grading.

Controlan la representación JSON de los modelos de calificaciones, asistencia
e incidentes de conducta.
"""

from rest_framework import serializers

from ..models import Attendance, ConductIncident, StudentNote


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

