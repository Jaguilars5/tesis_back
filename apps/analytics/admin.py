"""
Panel administrativo para el módulo Analytics.
"""

from django.contrib import admin
from .models import StudentRiskScore, StudentFeatureSnapshot


@admin.register(StudentRiskScore)
class StudentRiskScoreAdmin(admin.ModelAdmin):
    list_display = ("student", "academic_period", "risk_score", "risk_label", "calculated_at")
    list_filter = ("risk_label", "academic_period")
    search_fields = ("student__names", "student__last_names")


@admin.register(StudentFeatureSnapshot)
class StudentFeatureSnapshotAdmin(admin.ModelAdmin):
    list_display = ("student", "academic_period", "avg_grade_normalized", "attendance_rate", "calculated_at")
    list_filter = ("academic_period",)
    search_fields = ("student__names", "student__last_names")
