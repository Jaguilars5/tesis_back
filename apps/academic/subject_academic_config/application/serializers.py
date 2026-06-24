from rest_framework import serializers

from ..infrastructure.models import SubjectAcademicConfig


class SubjectAcademicConfigSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    academic_grade_name = serializers.CharField(
        source="academic_grade.name", read_only=True
    )

    class Meta:
        model = SubjectAcademicConfig
        fields = [
            "id",
            "subject",
            "academic_grade",
            "weekly_hours",
            "is_required",
            "is_active",
            "subject_name",
            "academic_grade_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
