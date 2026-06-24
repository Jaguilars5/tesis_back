from decimal import Decimal

from apps.core.repositories.base import BaseRepository

from .models import StudentNote, PeriodGradeSummary


class StudentNoteRepository(BaseRepository):
    model = StudentNote

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only)
        return queryset.order_by("-id")

    @classmethod
    def get_by_composite_key(cls, enrollment_id, evaluative_activity_id):
        return cls.model.objects.filter(
            enrollment_id=enrollment_id,
            evaluative_activity_id=evaluative_activity_id,
        ).first()

    @classmethod
    def list_by_filters(cls, student_id=None, academic_period_id=None, subject_id=None, section_id=None):
        queryset = cls.model.objects.all()
        if student_id:
            queryset = queryset.filter(enrollment__student_id=student_id)
        if academic_period_id:
            queryset = queryset.filter(
                evaluative_activity__block_component__evaluation_block__academic_period_id=academic_period_id
            )
        if subject_id:
            queryset = queryset.filter(
                evaluative_activity__teacher_subject_section__subject_offering__subject_academic_config__subject_id=subject_id
            )
        if section_id:
            queryset = queryset.filter(enrollment__section_id=section_id)
        return queryset.order_by("-created_at")

    @classmethod
    def list_for_risk_snapshot(cls, student_id, academic_period_id):
        return (
            cls.model.objects.filter(
                enrollment__student_id=student_id,
                evaluative_activity__block_component__evaluation_block__academic_period_id=academic_period_id,
            )
            .select_related(
                "evaluative_activity__teacher_subject_section__subject_offering__subject_academic_config__subject",
                "enrollment__student",
            )
            .order_by("created_at")
        )


class PeriodGradeSummaryRepository(BaseRepository):
    model = PeriodGradeSummary

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("-id")

    @classmethod
    def get_by_enrollment(cls, enrollment_id):
        return cls.model.objects.filter(
            enrollment_id=enrollment_id,
        ).select_related("subject_offering", "academic_period", "qualitative_scale")

    @classmethod
    def get_by_enrollment_offering_period(cls, enrollment, subject_offering, academic_period):
        return cls.model.objects.filter(
            enrollment=enrollment,
            subject_offering=subject_offering,
            academic_period=academic_period,
        ).first()

    @classmethod
    def get_failing(cls, academic_period_id):
        return cls.model.objects.filter(
            academic_period_id=academic_period_id,
            is_failing=True,
        ).select_related("enrollment__student", "subject_offering")

    @classmethod
    def count_failing(cls, enrollment_id, academic_period_id):
        return cls.model.objects.filter(
            enrollment_id=enrollment_id,
            academic_period_id=academic_period_id,
            is_failing=True,
        ).count()


class EvaluationRepository:
    """M\u00e9todos de acceso a datos para c\u00e1lculos de evaluaci\u00f3n."""

    @staticmethod
    def calculate_period_average_for_subject(enrollment_id, subject_offering_id):
        from django.db.models import Avg
        from .models import StudentNote

        result = StudentNote.objects.filter(
            enrollment_id=enrollment_id,
            evaluative_activity__teacher_subject_section__subject_offering_id=subject_offering_id,
        ).aggregate(avg=Avg("numeric_score"))
        avg = result.get("avg")
        if avg is None:
            return None
        return Decimal(str(avg)).quantize(Decimal("0.01"))
