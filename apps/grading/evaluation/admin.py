from django.contrib import admin

from .infrastructure.models import EvaluationBlock, BlockComponent, EvaluativeActivity, EvaluativeActivityChangeHistory


@admin.register(EvaluationBlock)
class EvaluationBlockAdmin(admin.ModelAdmin):
    list_display = ("name", "academic_period", "subject_offering", "block_type", "weight_percentage", "is_active")
    list_filter = ("block_type", "is_active", "academic_period")


@admin.register(BlockComponent)
class BlockComponentAdmin(admin.ModelAdmin):
    list_display = ("name", "evaluation_block", "internal_weight", "is_active")
    list_filter = ("is_active",)


@admin.register(EvaluativeActivityChangeHistory)
class EvaluativeActivityChangeHistoryAdmin(admin.ModelAdmin):
    list_display = ("evaluative_activity", "previous_due_date", "new_due_date", "modified_by_user", "modified_at")
    list_filter = ("modified_at",)
    search_fields = ("reason",)


@admin.register(EvaluativeActivity)
class EvaluativeActivityAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher_subject_section", "activity_type", "max_score", "due_date", "is_active")
    list_filter = ("is_active", "activity_type", "due_date")
