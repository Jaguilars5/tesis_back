"""
Panel administrativo para el módulo Analytics.
"""

from django.contrib import admin
from .models import StudentRiskScore, StudentFeatureSnapshot, EarlyAlert, RiskFactor, StudentRiskFactor


@admin.register(StudentRiskScore)
class StudentRiskScoreAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "academic_period", "risk_score", "risk_label", "calculated_at")
    list_filter = ("risk_label", "academic_period")
    search_fields = ("enrollment__student__person__names", "enrollment__student__person__last_names")


@admin.register(StudentFeatureSnapshot)
class StudentFeatureSnapshotAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "academic_period", "formative_avg_normalized", "summative_avg_normalized", "attendance_rate", "calculated_at")
    list_filter = ("academic_period",)
    search_fields = ("enrollment__student__person__names", "enrollment__student__person__last_names")


@admin.register(EarlyAlert)
class EarlyAlertAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "academic_period", "alert_type", "urgency_level", "attended", "detected_at")
    list_filter = ("alert_type", "urgency_level", "attended", "academic_period")
    search_fields = ("enrollment__student__person__names", "enrollment__student__person__last_names", "description")


@admin.register(RiskFactor)
class RiskFactorAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "description")
    search_fields = ("code", "name")


@admin.register(StudentRiskFactor)
class StudentRiskFactorAdmin(admin.ModelAdmin):
    list_display = ("student_risk_score", "risk_factor", "contribution_weight")
    list_filter = ("risk_factor",)


