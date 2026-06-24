from rest_framework import serializers

from ..infrastructure.models import TeacherSubjectSection


class TeacherSubjectSectionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(
        source="user.person.get_full_name", read_only=True
    )
    subject_offering_name = serializers.SerializerMethodField()
    subject_offering_school_year = serializers.IntegerField(
        source="subject_offering.section.school_year_id", read_only=True
    )
    subject_offering_school_year_name = serializers.CharField(
        source="subject_offering.section.school_year.name", read_only=True
    )
    subject_offering_section = serializers.IntegerField(
        source="subject_offering.section_id", read_only=True
    )
    subject_offering_section_name = serializers.CharField(
        source="subject_offering.section.__str__", read_only=True
    )
    subject_offering_academic_grade = serializers.IntegerField(
        source="subject_offering.section.academic_grade_id",
        read_only=True,
        allow_null=True,
    )
    subject_offering_academic_grade_name = serializers.CharField(
        source="subject_offering.section.academic_grade.name",
        read_only=True,
        allow_null=True,
    )
    subject_offering_subject = serializers.IntegerField(
        source="subject_offering.subject_academic_config.subject_id", read_only=True
    )
    subject_offering_subject_name = serializers.CharField(
        source="subject_offering.subject_academic_config.subject.name", read_only=True
    )
    subject_offering_config = serializers.IntegerField(
        source="subject_offering.subject_academic_config_id", read_only=True
    )
    subject_offering_config_name = serializers.CharField(
        source="subject_offering.subject_academic_config.__str__", read_only=True
    )

    class Meta:
        model = TeacherSubjectSection
        fields = [
            "id",
            "user",
            "subject_offering",
            "is_active",
            "user_name",
            "subject_offering_name",
            "subject_offering_school_year",
            "subject_offering_school_year_name",
            "subject_offering_section",
            "subject_offering_section_name",
            "subject_offering_academic_grade",
            "subject_offering_academic_grade_name",
            "subject_offering_subject",
            "subject_offering_subject_name",
            "subject_offering_config",
            "subject_offering_config_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_subject_offering_name(self, obj):
        return str(obj.subject_offering)
