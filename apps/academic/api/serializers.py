from rest_framework import serializers
from ..models import (
    AcademicPeriod,
    PeriodType,
    Subject,
    SubjectAcademicConfig,
    SubjectOffering,
    TeacherSubjectSection,
)


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"


class AcademicPeriodSerializer(serializers.ModelSerializer):
    school_year_name = serializers.CharField(source="school_year.name", read_only=True)

    class Meta:
        model = AcademicPeriod
        fields = "__all__"


class TeacherSubjectSectionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(
        source="user.person.get_full_name", read_only=True
    )
    subject_offering_name = serializers.CharField(
        source="subject_offering.__str__", read_only=True
    )

    class Meta:
        model = TeacherSubjectSection
        fields = "__all__"


class SubjectAcademicConfigSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    academic_grade_name = serializers.CharField(
        source="academic_grade.name", read_only=True
    )

    class Meta:
        model = SubjectAcademicConfig
        fields = "__all__"


class SubjectOfferingSerializer(serializers.ModelSerializer):
    school_year_name = serializers.CharField(source="school_year.name", read_only=True)
    section_name = serializers.CharField(source="section.__str__", read_only=True)
    subject_academic_config_name = serializers.CharField(
        source="subject_academic_config.__str__", read_only=True
    )

    class Meta:
        model = SubjectOffering
        fields = "__all__"


from ..models import InterdisciplinaryProject, SubjectProject


class SubjectProjectSerializer(serializers.ModelSerializer):
    interdisciplinary_project_title = serializers.CharField(
        source="interdisciplinary_project.title", read_only=True
    )
    subject_offering_name = serializers.CharField(
        source="subject_offering.__str__", read_only=True
    )

    class Meta:
        model = SubjectProject
        fields = "__all__"


class PeriodTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodType
        fields = "__all__"


class InterdisciplinaryProjectSerializer(serializers.ModelSerializer):
    academic_period_name = serializers.CharField(
        source="academic_period.name", read_only=True
    )
    subject_projects = SubjectProjectSerializer(many=True, read_only=True)

    class Meta:
        model = InterdisciplinaryProject
        fields = "__all__"
