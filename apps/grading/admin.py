from django.contrib import admin
from .models import (
    ActivityType,
    BlockComponent,
    EvaluationBlock,
    EvaluativeActivity,
    GradeChangeHistory,
    PeriodGradeSummary,
    QualitativeScale,
    StudentNote,
)


@admin.register(StudentNote)
class StudentNoteAdmin(admin.ModelAdmin):
    list_display = ("id", "enrollment", "evaluative_activity", "numeric_score", "sync_status", "created_at")
    list_filter = ("sync_status",)
    search_fields = ("enrollment__student__person__names",)


@admin.register(EvaluationBlock)
class EvaluationBlockAdmin(admin.ModelAdmin):
    list_display = ("name", "academic_period", "block_type", "weight_percentage", "is_active")
    list_filter = ("block_type", "is_active")


@admin.register(BlockComponent)
class BlockComponentAdmin(admin.ModelAdmin):
    list_display = ("name", "evaluation_block", "internal_weight")


@admin.register(EvaluativeActivity)
class EvaluativeActivityAdmin(admin.ModelAdmin):
    list_display = ("title", "activity_type", "block_component", "max_score", "internal_weight", "due_date")
    list_filter = ("activity_type",)


@admin.register(GradeChangeHistory)
class GradeChangeHistoryAdmin(admin.ModelAdmin):
    list_display = ("student_note", "previous_score", "new_score", "modified_at")


@admin.register(PeriodGradeSummary)
class PeriodGradeSummaryAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "subject_offering", "academic_period", "final_avg_truncated", "promotion_status")
    list_filter = ("academic_period", "promotion_status")
    search_fields = ("enrollment__student__person__names", "subject_offering__subject_academic_config__subject__name")


@admin.register(QualitativeScale)
class QualitativeScaleAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "numeric_equivalence", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name", "description")


@admin.register(ActivityType)
class ActivityTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
