from django.contrib import admin
from .models import (
    Attendance, AttendanceStatus, BehaviorEvaluation, ClassAssignment,
    ConductIncident, EvaluationCriteria, EvaluationMacro, EvaluationSubcriteria,
    GradeChangeHistory, GradeType, QualitativeScale, StudentNote,
)


@admin.register(StudentNote)
class StudentNoteAdmin(admin.ModelAdmin):
    list_display = ("id", "enrollment", "class_assignment", "grade_type", "numeric_score", "sync_status", "created_at")
    list_filter = ("grade_type", "sync_status")
    search_fields = ("enrollment__student__person__names",)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("id", "enrollment", "attendance_date", "attendance_status", "created_at")
    list_filter = ("attendance_status", "attendance_date")
    search_fields = ("enrollment__student__person__names",)


@admin.register(ConductIncident)
class ConductIncidentAdmin(admin.ModelAdmin):
    list_display = ("id", "enrollment", "category", "severity", "incident_date", "family_notified")
    list_filter = ("category", "severity", "incident_date")
    search_fields = ("enrollment__student__person__names", "description")


@admin.register(BehaviorEvaluation)
class BehaviorEvaluationAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "academic_period", "calculated_scale", "final_scale")


@admin.register(AttendanceStatus)
class AttendanceStatusAdmin(admin.ModelAdmin):
    list_display = ("code", "name")


@admin.register(GradeType)
class GradeTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "name")


@admin.register(QualitativeScale)
class QualitativeScaleAdmin(admin.ModelAdmin):
    list_display = ("code", "description", "numeric_equivalence")


@admin.register(EvaluationMacro)
class EvaluationMacroAdmin(admin.ModelAdmin):
    list_display = ("name", "academic_period", "weight_percentage", "active")


@admin.register(EvaluationCriteria)
class EvaluationCriteriaAdmin(admin.ModelAdmin):
    list_display = ("name", "evaluation_macro", "internal_weight")


@admin.register(EvaluationSubcriteria)
class EvaluationSubcriteriaAdmin(admin.ModelAdmin):
    list_display = ("name", "evaluation_criteria", "internal_weight")


@admin.register(ClassAssignment)
class ClassAssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "evaluation_subcriteria", "max_score", "due_date")


@admin.register(GradeChangeHistory)
class GradeChangeHistoryAdmin(admin.ModelAdmin):
    list_display = ("student_note", "previous_score", "new_score", "modified_at")
