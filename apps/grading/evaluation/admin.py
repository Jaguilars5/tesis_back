from django.contrib import admin

from .infrastructure.models import EvaluationBlock, BlockComponent, EvaluativeActivity


@admin.register(EvaluationBlock)
class EvaluationBlockAdmin(admin.ModelAdmin):
    list_display = ("name", "academic_period", "subject_offering", "block_type", "weight_percentage", "is_active")
    list_filter = ("block_type", "is_active", "academic_period")


@admin.register(BlockComponent)
class BlockComponentAdmin(admin.ModelAdmin):
    list_display = ("name", "evaluation_block", "internal_weight", "is_active")
    list_filter = ("is_active",)


@admin.register(EvaluativeActivity)
class EvaluativeActivityAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher_subject_section", "activity_type", "max_score", "due_date", "is_active")
    list_filter = ("is_active", "activity_type", "due_date")
