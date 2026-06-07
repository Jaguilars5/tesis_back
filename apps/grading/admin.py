from django.contrib import admin
from .models import (
    BlockComponent,
    ComponentIndicator,
    DiagnosticEvaluation,
    EvaluationBlock,
    EvaluativeActivity,
    GradeChangeHistory,
    GradeType,
    PeriodGradeSummary,
    ProjectNote,
    QualitativeScale,
    RecoveryProcess,
    StudentNote,
)


@admin.register(StudentNote)
class StudentNoteAdmin(admin.ModelAdmin):
    list_display = ("id", "enrollment", "evaluative_activity", "grade_type", "numeric_score", "sync_status", "created_at")
    list_filter = ("grade_type", "sync_status")
    search_fields = ("enrollment__student__person__names",)


@admin.register(GradeType)
class GradeTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "applies_to_sublevel")


@admin.register(QualitativeScale)
class QualitativeScaleAdmin(admin.ModelAdmin):
    list_display = ("code", "description", "numeric_equivalence", "applicable_sublevel")


@admin.register(EvaluationBlock)
class EvaluationBlockAdmin(admin.ModelAdmin):
    list_display = ("name", "academic_period", "evaluation_type", "weight_percentage", "active")
    list_filter = ("evaluation_type", "active")


@admin.register(BlockComponent)
class BlockComponentAdmin(admin.ModelAdmin):
    list_display = ("name", "evaluation_block", "internal_weight")


@admin.register(ComponentIndicator)
class ComponentIndicatorAdmin(admin.ModelAdmin):
    list_display = ("name", "block_component", "internal_weight")


@admin.register(EvaluativeActivity)
class EvaluativeActivityAdmin(admin.ModelAdmin):
    list_display = ("title", "activity_type", "component_indicator", "max_score", "due_date", "is_interdisciplinary_project")
    list_filter = ("activity_type", "is_interdisciplinary_project")


@admin.register(GradeChangeHistory)
class GradeChangeHistoryAdmin(admin.ModelAdmin):
    list_display = ("student_note", "previous_score", "new_score", "modified_at")


@admin.register(PeriodGradeSummary)
class PeriodGradeSummaryAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "subject_offering", "academic_period", "final_avg_truncated", "promotion_status")
    list_filter = ("academic_period", "promotion_status")
    search_fields = ("enrollment__student__person__names", "subject_offering__subject_academic_config__subject__name")


@admin.register(RecoveryProcess)
class RecoveryProcessAdmin(admin.ModelAdmin):
    list_display = ("period_grade_summary", "process_type", "initial_grade", "final_calculated_grade", "start_date")
    list_filter = ("process_type", "family_notified")
    search_fields = ("period_grade_summary__enrollment__student__person__names",)


@admin.register(DiagnosticEvaluation)
class DiagnosticEvaluationAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "academic_period", "socioemotional_area", "development_level", "application_date")
    list_filter = ("academic_period", "development_level")
    search_fields = ("enrollment__student__person__names", "socioemotional_area")


@admin.register(ProjectNote)
class ProjectNoteAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "interdisciplinary_project", "final_score", "created_at")
    list_filter = ("sync_status",)
    search_fields = ("enrollment__student__person__names", "interdisciplinary_project__title")
