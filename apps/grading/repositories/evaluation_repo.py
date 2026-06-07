from decimal import Decimal
from django.db import models
from ..models import (
    EvaluationBlock,
    BlockComponent,
    ComponentIndicator,
    EvaluativeActivity,
    StudentNote,
    GradeChangeHistory,
)


class EvaluationRepository:
    @staticmethod
    def get_block_with_hierarchy(block_id):
        """Retorna un EvaluationBlock con toda su jerarquía precargada."""
        return EvaluationBlock.objects.filter(id=block_id).prefetch_related(
            models.Prefetch(
                "components",
                queryset=BlockComponent.objects.prefetch_related(
                    models.Prefetch(
                        "indicators",
                        queryset=ComponentIndicator.objects.prefetch_related("activities"),
                    )
                ),
            )
        ).first()

    @staticmethod
    def get_notes_for_block(enrollment_id, block_id):
        """Notas del estudiante para todas las actividades de un bloque de evaluación."""
        return StudentNote.objects.filter(
            enrollment_id=enrollment_id,
            evaluative_activity__component_indicator__block_component__evaluation_block_id=block_id,
        ).select_related(
            "evaluative_activity__component_indicator__block_component__evaluation_block"
        )

    @staticmethod
    def get_notes_for_period(enrollment_id, period_id):
        """Notas del estudiante para todos los bloques de un período académico."""
        return StudentNote.objects.filter(
            enrollment_id=enrollment_id,
            evaluative_activity__component_indicator__block_component__evaluation_block__academic_period_id=period_id,
        ).select_related("evaluative_activity")

    @staticmethod
    def get_grade_history(note_id):
        return GradeChangeHistory.objects.filter(student_note_id=note_id).order_by("-modified_at")

    @staticmethod
    def record_grade_change(note, new_score, user_id=None, reason=""):
        previous = note.numeric_score
        history = GradeChangeHistory.objects.create(
            student_note=note,
            modified_by_user_id=user_id,
            previous_score=previous,
            new_score=new_score,
            reason=reason,
        )
        note.numeric_score = new_score
        note.manually_overridden = True
        note.save()
        return history

    @staticmethod
    def calculate_block_average(enrollment_id, block_id):
        """Calcula el promedio ponderado del estudiante en un bloque de evaluación."""
        notes = EvaluationRepository.get_notes_for_block(enrollment_id, block_id)
        if not notes:
            return None

        total_score = Decimal("0.00")
        total_weight = Decimal("0.00")

        for note in notes:
            activity = note.evaluative_activity
            indicator = activity.component_indicator
            component = indicator.block_component

            ind_weight = indicator.internal_weight
            comp_weight = component.internal_weight

            if activity.max_score > 0:
                normalized = (note.numeric_score / activity.max_score) * Decimal("10")
            else:
                normalized = Decimal("0.00")

            combined = (ind_weight / Decimal("100")) * (comp_weight / Decimal("100"))
            total_score += normalized * combined
            total_weight += combined

        return (total_score / total_weight).quantize(Decimal("0.01")) if total_weight > 0 else None

    @staticmethod
    def calculate_period_average_for_subject(enrollment_id, subject_offering_id):
        """
        Calcula el promedio ponderado de un estudiante para una oferta de asignatura
        en un período completo, usando la jerarquía de evaluación.
        """
        notes = StudentNote.objects.filter(
            enrollment_id=enrollment_id,
            evaluative_activity__teacher_subject_section__subject_offering_id=subject_offering_id,
            manually_overridden=False,
        ).select_related(
            "evaluative_activity__component_indicator__block_component__evaluation_block"
        )

        if not notes.exists():
            return None

        total_score = Decimal("0.00")
        total_weight = Decimal("0.00")

        for note in notes:
            activity = note.evaluative_activity
            max_score = activity.max_score or Decimal("1.00")
            normalized = (note.numeric_score / max_score) * Decimal("10")

            indicator = activity.component_indicator
            component = indicator.block_component
            block = component.evaluation_block

            ind_weight = indicator.internal_weight / Decimal("100")
            comp_weight = component.internal_weight / Decimal("100")
            block_weight = block.weight_percentage / Decimal("100")

            combined = ind_weight * comp_weight * block_weight
            total_score += normalized * combined
            total_weight += combined

        if total_weight == 0:
            return None

        return (total_score / total_weight).quantize(Decimal("0.01"))
