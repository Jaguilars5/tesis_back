"""
Panel administrativo para riesgo estudiantil.
"""

from django.contrib import admin

from .infrastructure.models import (
    RiskFactor,
    StudentRiskScore,
    StudentRiskFactor,
    StudentFeatureSnapshot,
    RiskScoringConfig,
)


@admin.register(RiskFactor)
class RiskFactorAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "description")
    search_fields = ("code", "name")


@admin.register(StudentRiskScore)
class StudentRiskScoreAdmin(admin.ModelAdmin):
    list_display = (
        "enrollment",
        "academic_period",
        "risk_score",
        "risk_label",
        "calculated_at",
    )
    list_filter = ("risk_label", "academic_period")
    search_fields = (
        "enrollment__student__user__person__names",
        "enrollment__student__user__person__last_names",
    )


@admin.register(StudentFeatureSnapshot)
class StudentFeatureSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        "enrollment",
        "academic_period",
        "formative_avg_normalized",
        "summative_avg_normalized",
        "attendance_rate",
        "calculated_at",
    )
    list_filter = ("academic_period",)
    search_fields = (
        "enrollment__student__user__person__names",
        "enrollment__student__user__person__last_names",
    )


@admin.register(StudentRiskFactor)
class StudentRiskFactorAdmin(admin.ModelAdmin):
    list_display = ("student_risk_score", "risk_factor", "contribution_weight")
    list_filter = ("risk_factor",)


# RiskScoringConfig es un singleton - no se registra en admin
# Se maneja vía API
