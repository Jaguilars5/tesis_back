from django.contrib import admin

from .infrastructure.models import BehaviorEvaluation


@admin.register(BehaviorEvaluation)
class BehaviorEvaluationAdmin(admin.ModelAdmin):
    list_display = ["enrollment", "academic_period", "calculated_scale", "final_scale"]
    list_filter = ["academic_period"]
