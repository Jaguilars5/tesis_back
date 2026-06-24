from django.contrib import admin

from .infrastructure.models import StudentNote, GradeChangeHistory, PeriodGradeSummary


@admin.register(StudentNote)
class StudentNoteAdmin(admin.ModelAdmin):
    list_display = ("id", "enrollment", "evaluative_activity", "numeric_score", "grading_mode", "manually_overridden")
    list_filter = ("grading_mode", "manually_overridden")
    search_fields = ("enrollment__student__user__person__names", "teacher_observation")


@admin.register(GradeChangeHistory)
class GradeChangeHistoryAdmin(admin.ModelAdmin):
    list_display = ("student_note", "previous_score", "new_score", "reason", "modified_at")
    list_filter = ("origin", "modified_at")
    search_fields = ("reason",)


@admin.register(PeriodGradeSummary)
class PeriodGradeSummaryAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "subject_offering", "academic_period", "final_avg_truncated", "is_failing")
    list_filter = ("is_failing", "academic_period")
