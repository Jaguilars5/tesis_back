from rest_framework import serializers
from ..models import (
    AcademicPeriod,
    ClassSchedule,
    PeriodType,
    Subject,
    SubjectAcademicConfig,
    SubjectOffering,
    TeacherSubjectSection,
)


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "name", "code", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class AcademicPeriodSerializer(serializers.ModelSerializer):
    school_year_name = serializers.CharField(source="school_year.name", read_only=True)
    period_type_name = serializers.CharField(
        source="period_type.name", read_only=True, allow_null=True
    )

    class Meta:
        model = AcademicPeriod
        fields = [
            "id",
            "code",
            "school_year",
            "name",
            "period_type",
            "start_date",
            "end_date",
            "year_weight",
            "is_regular_period",
            "is_active",
            "school_year_name",
            "period_type_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TeacherSubjectSectionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(
        source="user.person.get_full_name", read_only=True
    )
    subject_offering_name = serializers.SerializerMethodField()

    # Campos desglosados de la oferta de materia (para filtros server-side y UI)
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
        source="subject_offering.section.academic_grade_id", read_only=True,
        allow_null=True
    )
    subject_offering_academic_grade_name = serializers.CharField(
        source="subject_offering.section.academic_grade.name", read_only=True,
        allow_null=True
    )
    subject_offering_subject = serializers.IntegerField(
        source="subject_offering.subject_academic_config.subject_id",
        read_only=True
    )
    subject_offering_subject_name = serializers.CharField(
        source="subject_offering.subject_academic_config.subject.name",
        read_only=True
    )
    subject_offering_config = serializers.IntegerField(
        source="subject_offering.subject_academic_config_id", read_only=True
    )
    subject_offering_config_name = serializers.CharField(
        source="subject_offering.subject_academic_config.__str__",
        read_only=True
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


class SubjectOfferingSerializer(serializers.ModelSerializer):
    school_year = serializers.IntegerField(
        source="section.school_year_id", read_only=True
    )
    school_year_name = serializers.CharField(source="school_year.name", read_only=True)
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
        source="teacher_subject_section.subject_offering.section_id",
        read_only=True,
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
        source="teacher_subject_section.user_id",
        read_only=True,
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


class PeriodTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodType
        fields = [
            "id",
            "code",
            "name",
            "description",
            "divisions_per_year",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
