from rest_framework import serializers
from apps.attendance.models import (
    Attendance,
    AttendanceStatus,
    IncidentType,
    ConductIncident,
    SocioemotionalSkill,
    SkillEvaluation,
    BehaviorEvaluation,
)


class AttendanceStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceStatus
        fields = "__all__"


class IncidentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentType
        fields = "__all__"


class SocioemotionalSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocioemotionalSkill
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


class ConductIncidentSerializer(serializers.ModelSerializer):
    enrollment_name = serializers.CharField(source="enrollment.__str__", read_only=True)
    reported_by_user_name = serializers.CharField(
        source="reported_by_user.person.get_full_name", read_only=True
    )
    academic_period_name = serializers.CharField(
        source="academic_period.name", read_only=True
    )
    incident_type_name = serializers.CharField(
        source="incident_type.name", read_only=True
    )

    class Meta:
        model = ConductIncident
        fields = "__all__"
        read_only_fields = ["uuid", "created_at", "updated_at", "sync_version"]


class SkillEvaluationSerializer(serializers.ModelSerializer):
    enrollment_name = serializers.CharField(source="enrollment.__str__", read_only=True)
    academic_period_name = serializers.CharField(
        source="academic_period.name", read_only=True
    )
    socioemotional_skill_name = serializers.CharField(
        source="socioemotional_skill.name", read_only=True
    )
    qualitative_scale_name = serializers.CharField(
        source="qualitative_scale.name", read_only=True
    )

    class Meta:
        model = SkillEvaluation
        fields = "__all__"


class BehaviorEvaluationSerializer(serializers.ModelSerializer):
    enrollment_name = serializers.CharField(source="enrollment.__str__", read_only=True)
    academic_period_name = serializers.CharField(
        source="academic_period.name", read_only=True
    )
    calculated_scale_name = serializers.CharField(
        source="calculated_scale.name", read_only=True
    )
    final_scale_name = serializers.CharField(source="final_scale.name", read_only=True)

    class Meta:
        model = BehaviorEvaluation
        fields = "__all__"
