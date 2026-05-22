from rest_framework import serializers
from ..models import (
    Section, Subject, Academic_Period,
    Teacher_Subject_Section,
    SubjectAcademicConfig, SubjectOffering,
)

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class Academic_PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Academic_Period
        fields = '__all__'

class Teacher_Subject_SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher_Subject_Section
        fields = '__all__'

class SubjectAcademicConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectAcademicConfig
        fields = '__all__'

class SubjectOfferingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectOffering
        fields = '__all__'
