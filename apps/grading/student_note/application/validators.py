"""
Validaciones de negocio para StudentNote.
"""

from django.utils import timezone


def validate_required_fields(data, required):
    errors = {}
    for field in required:
        if field not in data or data[field] is None:
            errors[field] = f"{field} es obligatorio"
    return errors


def validate_numeric_score(value):
    if value is not None and value < 0:
        return {"numeric_score": "La nota no puede ser negativa"}
    return {}


def has_registered_grade(note) -> bool:
    if note is None or note.manually_overridden:
        return False
    return note.numeric_score is not None or note.qualitative_scale_id is not None


def is_score_changing(note, numeric_score, qualitative_scale_id) -> bool:
    if note is None:
        return numeric_score is not None or qualitative_scale_id is not None
    if numeric_score is not None and note.numeric_score != numeric_score:
        return True
    if qualitative_scale_id is not None and note.qualitative_scale_id != qualitative_scale_id:
        return True
    return False


def validate_grading_window(evaluative_activity, *, existing_note=None, is_score_change=False):
    """
    Valida que la calificación se realice dentro del período académico y,
    si se modifica una nota ya registrada, dentro de la fecha de entrega.
    """
    if not evaluative_activity:
        return {}

    today = timezone.localdate()
    period = evaluative_activity.block_component.evaluation_block.academic_period

    if getattr(period, "grades_locked", False):
        return {
            "grading": "El período académico está cerrado para calificaciones"
        }

    if today < period.start_date or today > period.end_date:
        return {
            "grading": (
                f"No se pueden registrar calificaciones fuera del período académico "
                f"({period.start_date} - {period.end_date})"
            )
        }

    if (
        is_score_change
        and has_registered_grade(existing_note)
        and today > evaluative_activity.due_date
    ):
        return {
            "grading": (
                "La fecha de entrega ya pasó. "
                "Modifique la fecha de la actividad para poder cambiar la nota."
            )
        }

    return {}


def run_all_validators(**kwargs):
    errors = {}
    errors.update(validate_required_fields(kwargs, [
        "enrollment_id", "evaluative_activity_id",
    ]))
    errors.update(validate_numeric_score(kwargs.get("numeric_score")))
    evaluative_activity = kwargs.get("evaluative_activity")
    existing_note = kwargs.get("existing_note")
    is_score_change = kwargs.get("is_score_change", False)
    if evaluative_activity:
        errors.update(validate_grading_window(
            evaluative_activity,
            existing_note=existing_note,
            is_score_change=is_score_change,
        ))
    return errors
