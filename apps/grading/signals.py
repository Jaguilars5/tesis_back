"""
Signals para el modulo Grading.

Mantenimiento automatico de PeriodGradeSummary (cache denormalizado) en respuesta
a cambios en StudentNote.

Cadena de dependencias:
    StudentNote  --post_save/post_delete-->  PeriodGradeSummary  --read-->  Analytics/Risk

Una nota cambiada recalcula UN solo (enrollment, subject_offering, period).
Las operaciones masivas (bulk_create, queryset.update, seeds, importadores)
deben envolverse en `skip_period_summary_recalc()` para evitar miles de tasks.
"""

import contextlib
import logging
import threading

from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import StudentNote
from .tasks import recompute_period_grade_summary_task


logger = logging.getLogger(__name__)


_local = threading.local()


def _bulk_flag_active() -> bool:
    return getattr(_local, "skip_recalc", False)


@contextlib.contextmanager
def skip_period_summary_recalc():
    """
    Context manager que suprime el recalculo automatico del resumen.

    Uso:
        with skip_period_summary_recalc():
            StudentNote.objects.bulk_create(notes)
    """
    prev = getattr(_local, "skip_recalc", False)
    _local.skip_recalc = True
    try:
        yield
    finally:
        _local.skip_recalc = prev


def _enqueue_recompute(note):
    """
    Despacha la task Celery para recalcular el resumen correspondiente.
    Usa transaction.on_commit para no calcular sobre notas que haran rollback.
    """
    if _bulk_flag_active():
        return
    if not (note.enrollment_id and note.evaluative_activity_id):
        return

    try:
        activity = note.evaluative_activity
        block = activity.block_component.evaluation_block
    except Exception:  # pragma: no cover - defensive
        logger.exception("No se pudo resolver la jerarquia de bloques para la nota %s", note.pk)
        return

    enrollment_id = note.enrollment_id
    offering_id = block.subject_offering_id
    period_id = block.academic_period_id

    transaction.on_commit(
        lambda: recompute_period_grade_summary_task.delay(
            enrollment_id, offering_id, period_id
        )
    )


@receiver(post_save, sender=StudentNote)
def student_note_post_save(sender, instance, created, **kwargs):
    _enqueue_recompute(instance)


@receiver(post_delete, sender=StudentNote)
def student_note_post_delete(sender, instance, **kwargs):
    _enqueue_recompute(instance)
