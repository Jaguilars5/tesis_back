from rest_framework import serializers


class OverviewSerializer(serializers.Serializer):
    total_students = serializers.IntegerField()
    active_enrollments = serializers.IntegerField()
    at_risk_count = serializers.IntegerField()
    alert_count = serializers.IntegerField()
    avg_attendance = serializers.FloatField(allow_null=True)


class RiskDistributionSerializer(serializers.Serializer):
    grade_name = serializers.CharField()
    green_count = serializers.IntegerField()
    yellow_count = serializers.IntegerField()
    red_count = serializers.IntegerField()
    total = serializers.IntegerField()


class StudentsAtRiskSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    student_name = serializers.CharField()
    risk_label = serializers.CharField()
    risk_score = serializers.FloatField()
    section_name = serializers.CharField(allow_null=True)


class SectionSummarySerializer(serializers.Serializer):
    section_id = serializers.IntegerField()
    section_name = serializers.CharField()
    total_students = serializers.IntegerField()
    at_risk_count = serializers.IntegerField()
    avg_attendance = serializers.FloatField(allow_null=True)


class RecalculatePeriodSerializer(serializers.Serializer):
    academic_period_id = serializers.IntegerField()
