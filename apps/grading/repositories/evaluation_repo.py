from decimal import Decimal
from django.db import models
from ..models import EvaluationMacro, EvaluationCriteria, EvaluationSubcriteria, ClassAssignment, StudentNote, GradeChangeHistory


class EvaluationRepository:
    @staticmethod
    def get_macro_with_hierarchy(macro_id):
        return EvaluationMacro.objects.filter(id=macro_id).prefetch_related(
            models.Prefetch(
                "criteria",
                queryset=EvaluationCriteria.objects.prefetch_related(
                    models.Prefetch(
                        "subcriteria",
                        queryset=EvaluationSubcriteria.objects.prefetch_related("assignments"),
                    )
                ),
            )
        ).first()

    @staticmethod
    def get_notes_for_macro(enrollment_id, macro_id):
        return StudentNote.objects.filter(
            enrollment_id=enrollment_id,
            class_assignment__evaluation_subcriteria__evaluation_criteria__evaluation_macro_id=macro_id,
        ).select_related("class_assignment__evaluation_subcriteria__evaluation_criteria__evaluation_macro")

    @staticmethod
    def get_notes_for_period(enrollment_id, period_id):
        return StudentNote.objects.filter(
            enrollment_id=enrollment_id,
            class_assignment__evaluation_subcriteria__evaluation_criteria__evaluation_macro__academic_period_id=period_id,
        ).select_related("class_assignment")

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
    def calculate_macro_average(enrollment_id, macro_id):
        notes = EvaluationRepository.get_notes_for_macro(enrollment_id, macro_id)
        if not notes:
            return None

        total_score = Decimal("0.00")
        total_weight = Decimal("0.00")

        for note in notes:
            assignment = note.class_assignment
            sub = assignment.evaluation_subcriteria
            crit = sub.evaluation_criteria

            sub_weight = sub.internal_weight
            crit_weight = crit.internal_weight

            normalized = (note.numeric_score / assignment.max_score * Decimal("10")) if assignment.max_score > 0 else Decimal("0.00")
            combined = (sub_weight / Decimal("100")) * (crit_weight / Decimal("100"))
            total_score += normalized * combined
            total_weight += combined

        return (total_score / total_weight).quantize(Decimal("0.01")) if total_weight > 0 else None
