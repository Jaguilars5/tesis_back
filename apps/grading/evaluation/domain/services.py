import logging
from decimal import Decimal

from django.db import transaction

from ..application import validators

logger = logging.getLogger(__name__)
from ..infrastructure.repositories import (
    EvaluationBlockRepository,
    BlockComponentRepository,
    EvaluativeActivityRepository,
)


class EvaluationService:
    """Logica de negocio para bloques, componentes y actividades evaluativas."""

    repository_block = EvaluationBlockRepository
    repository_component = BlockComponentRepository
    repository_activity = EvaluativeActivityRepository

    @classmethod
    def _resolve_academic_period(cls, block_component_id):
        component = cls.repository_component.get_by_id(block_component_id)
        if not component:
            return None
        block = cls.repository_block.get_by_id(component.evaluation_block_id)
        if not block:
            return None
        return block.academic_period

    @classmethod
    def create_evaluative_activity(cls, block_component_id=None, teacher_subject_section_id=None, **kwargs):
        academic_period = None
        if block_component_id:
            academic_period = cls._resolve_academic_period(block_component_id)

        errors = validators.run_all_validators(
            block_component_id=block_component_id,
            teacher_subject_section_id=teacher_subject_section_id,
            academic_period=academic_period,
            **kwargs,
        )
        if errors:
            raise ValueError(errors)

        if not block_component_id and teacher_subject_section_id:
            from apps.academic.teacher_subject_section.infrastructure.models import (
                TeacherSubjectSection,
            )
            try:
                tss = TeacherSubjectSection.objects.get(pk=teacher_subject_section_id)
                component = cls.repository_component.get_active_component_for_offering(
                    tss.subject_offering_id
                )
                if not component:
                    raise ValueError(
                        "No existe un componente de bloque activo para esta clase. "
                        "Configure los bloques de evaluacion primero."
                    )
                block_component_id = component.id
            except TeacherSubjectSection.DoesNotExist:
                raise ValueError("teacher_subject_section no encontrado")
            academic_period = cls._resolve_academic_period(block_component_id)
            errors = validators.run_all_validators(
                block_component_id=block_component_id,
                teacher_subject_section_id=teacher_subject_section_id,
                academic_period=academic_period,
                **kwargs,
            )
            if errors:
                raise ValueError(errors)

        activity = cls.repository_activity.create(
            block_component_id=block_component_id,
            teacher_subject_section_id=teacher_subject_section_id,
            **kwargs,
        )

        cls._enqueue_activity_created_notification(activity)
        return activity

    @classmethod
    @transaction.atomic
    def update_evaluative_activity(cls, activity_id, user_id=None, reason="", **kwargs):
        from ..infrastructure.models import EvaluativeActivityChangeHistory

        activity = cls.repository_activity.get_by_id(activity_id)
        if not activity:
            raise ValueError(f"Actividad evaluativa {activity_id} no encontrada")

        period = activity.block_component.evaluation_block.academic_period
        due_date = kwargs.get("due_date", activity.due_date)

        errors = validators.run_activity_update_validators(
            academic_period=period,
            due_date=due_date,
        )
        if errors:
            raise ValueError(errors)

        previous_due_date = activity.due_date
        clean = {k: v for k, v in kwargs.items() if v is not None}
        updated = cls.repository_activity.update(activity_id, **clean)

        if "due_date" in clean and clean["due_date"] != previous_due_date:
            EvaluativeActivityChangeHistory.objects.create(
                evaluative_activity=updated,
                modified_by_user_id=user_id,
                previous_due_date=previous_due_date,
                new_due_date=clean["due_date"],
                reason=reason or "Cambio de fecha de entrega",
            )

        return updated

    @staticmethod
    def _enqueue_activity_created_notification(activity):
        try:
            from apps.core.notifications.tasks import notify_activity_created

            transaction.on_commit(
                lambda: notify_activity_created.delay(activity.id)
            )
        except Exception:
            logger.warning(
                "No se pudo programar la notificación de actividad creada activity=%s",
                getattr(activity, "id", None),
                exc_info=True,
            )

    @classmethod
    def calculate_block_grade(cls, enrollment_id, evaluation_block_id):
        notes = cls.repository_activity.get_notes_for_block(enrollment_id, evaluation_block_id)
        if not notes:
            return None

        total_score = Decimal("0.00")
        total_weight = Decimal("0.00")

        for note in notes:
            activity = note.evaluative_activity
            component = activity.block_component

            act_weight = activity.internal_weight
            comp_weight = component.internal_weight

            if activity.max_score > 0:
                normalized = (note.numeric_score / activity.max_score) * Decimal("10")
            else:
                normalized = Decimal("0.00")

            combined_weight = (act_weight / Decimal("100")) * (comp_weight / Decimal("100"))
            total_score += normalized * combined_weight
            total_weight += combined_weight

        if total_weight == 0:
            return None

        weighted_avg = total_score / total_weight
        return weighted_avg.quantize(Decimal("0.01"))

    @classmethod
    def calculate_period_average(cls, enrollment_id, academic_period_id):
        blocks = cls.repository_block.get_blocks_for_period(academic_period_id)
        if not blocks:
            return None

        total_score = Decimal("0.00")
        total_weight = Decimal("0.00")

        for block in blocks:
            block_grade = cls.calculate_block_grade(enrollment_id, block.id)
            if block_grade is not None:
                total_score += block_grade * (block.weight_percentage / Decimal("100"))
                total_weight += block.weight_percentage / Decimal("100")

        if total_weight == 0:
            return None

        return (total_score / total_weight).quantize(Decimal("0.01"))

    @classmethod
    def soft_delete_block(cls, pk, confirm=False):
        obj = cls.repository_block.get_by_id(pk)
        if not obj:
            raise ValueError(f"Bloque de evaluacion {pk} no encontrado")
        counts = cls.repository_block.get_cascade_counts(pk)
        total = sum(counts.values())

        if total > 0 and not confirm:
            parts = [f"{v} {k}" for k, v in counts.items()]
            return {
                "requires_confirmation": True,
                "affected_records": total,
                "message": f"Esta accion desactivar\u00e1 {', '.join(parts)} relacionados",
                "id": obj.id,
                "is_active": True,
            }

        total = cls.repository_block.deactivate_cascade(pk)
        return {"id": obj.id, "is_active": False, "deactivated_records": total}

    @classmethod
    def soft_delete_component(cls, pk, confirm=False):
        obj = cls.repository_component.get_by_id(pk)
        if not obj:
            raise ValueError(f"Componente de bloque {pk} no encontrado")
        counts = cls.repository_component.get_cascade_counts(pk)
        total = sum(counts.values())

        if total > 0 and not confirm:
            parts = [f"{v} {k}" for k, v in counts.items()]
            return {
                "requires_confirmation": True,
                "affected_records": total,
                "message": f"Esta accion desactivar\u00e1 {', '.join(parts)} relacionados",
                "id": obj.id,
                "is_active": True,
            }

        total = cls.repository_component.deactivate_cascade(pk)
        return {"id": obj.id, "is_active": False, "deactivated_records": total}

    @classmethod
    def soft_delete_activity(cls, pk, confirm=False):
        obj = cls.repository_activity.get_by_id(pk)
        if not obj:
            raise ValueError(f"Actividad evaluativa {pk} no encontrada")
        counts = cls.repository_activity.get_cascade_counts(pk)
        total = sum(counts.values())

        if total > 0 and not confirm:
            parts = [f"{v} {k}" for k, v in counts.items()]
            return {
                "requires_confirmation": True,
                "affected_records": total,
                "message": f"Esta accion desactivar\u00e1 {', '.join(parts)} relacionados",
                "id": obj.id,
                "is_active": True,
            }

        total = cls.repository_activity.deactivate_cascade(pk)
        return {"id": obj.id, "is_active": False, "deactivated_records": total}

    @classmethod
    def get_grade_hierarchy(cls, evaluative_activity):
        component = evaluative_activity.block_component
        block = component.evaluation_block
        period = block.academic_period

        return {
            "evaluative_activity": evaluative_activity,
            "component": component,
            "block": block,
            "academic_period": period,
        }
