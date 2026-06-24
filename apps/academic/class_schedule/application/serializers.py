from rest_framework import serializers

from ..infrastructure.models import ClassSchedule


class ClassScheduleSerializer(serializers.ModelSerializer):
    subject_offering_name = serializers.CharField(
        source="teacher_subject_section.subject_offering.__str__", read_only=True
    )
    day_of_week_name = serializers.SerializerMethodField(read_only=True)
    section_name = serializers.CharField(
        source="teacher_subject_section.subject_offering.section.__str__",
        read_only=True,
    )
    section_id = serializers.IntegerField(
        source="teacher_subject_section.subject_offering.section_id", read_only=True
    )
    subject_name = serializers.CharField(
        source="teacher_subject_section.subject_offering.subject_academic_config.subject.name",
        read_only=True,
    )
    subject_id = serializers.IntegerField(
        source="teacher_subject_section.subject_offering.subject_academic_config.subject_id",
        read_only=True,
    )
    teacher_name = serializers.SerializerMethodField(read_only=True)
    teacher_id = serializers.IntegerField(
        source="teacher_subject_section.user_id", read_only=True
    )

    class Meta:
        model = ClassSchedule
        fields = [
            "id",
            "teacher_subject_section",
            "day_of_week",
            "start_time",
            "end_time",
            "is_active",
            "subject_offering_name",
            "day_of_week_name",
            "section_name",
            "section_id",
            "subject_name",
            "subject_id",
            "teacher_name",
            "teacher_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_day_of_week_name(self, obj):
        return obj.get_day_of_week_display()

    def get_teacher_name(self, obj):
        user = obj.teacher_subject_section.user
        return user.get_full_name()
