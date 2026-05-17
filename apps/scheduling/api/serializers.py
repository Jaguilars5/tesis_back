"""
Serializers de DRF para el módulo Scheduling.
"""

from rest_framework import serializers
from ..models import (
    ScheduleTemplateConfig,
    SubjectConstraint,
    ScheduleSlot,
    TeacherAvailability,
    TimeSlot,
)


class ScheduleTemplateConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleTemplateConfig
        fields = "__all__"


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = "__all__"


class TeacherAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherAvailability
        fields = "__all__"


class SubjectConstraintSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectConstraint
        fields = "__all__"


class ScheduleSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleSlot
        fields = "__all__"
