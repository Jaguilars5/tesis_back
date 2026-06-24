from rest_framework import serializers

from ..infrastructure.models import SubjectOffering


class SubjectOfferingSerializer(serializers.ModelSerializer):
    school_year = serializers.IntegerField(
        source="section.school_year_id", read_only=True
    )
    school_year_name = serializers.CharField(
        source="section.school_year.name", read_only=True
    )
    section_name = serializers.CharField(source="section.__str__", read_only=True)
    subject_academic_config_name = serializers.CharField(
        source="subject_academic_config.__str__", read_only=True
    )

    class Meta:
        model = SubjectOffering
        fields = [
            "id",
            "school_year",
            "section",
            "subject_academic_config",
            "is_active",
            "school_year_name",
            "section_name",
            "subject_academic_config_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
