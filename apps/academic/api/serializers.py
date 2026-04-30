from rest_framework import serializers
from ..models import (
    Section, Subject, Config_Academic, Academic_Period, 
    Academic_Activity, Timing_Regime, Teacher_Subject_Section
)

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class Config_AcademicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Config_Academic
        fields = '__all__'

class Academic_PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Academic_Period
        fields = '__all__'

class Academic_ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Academic_Activity
        fields = '__all__'

class Timing_RegimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timing_Regime
        fields = '__all__'

class Teacher_Subject_SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher_Subject_Section
        fields = '__all__'
