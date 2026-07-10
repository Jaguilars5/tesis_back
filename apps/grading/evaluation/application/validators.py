"""
Validaciones de negocio para EvaluationBlock, BlockComponent y EvaluativeActivity.
"""

from datetime import date


def validate_required_fields(data, required):
    errors = {}
    for field in required:
        if field not in data or data[field] is None:
            errors[field] = f"{field} es obligatorio"
        elif isinstance(data[field], str) and not data[field].strip():
            errors[field] = f"{field} no puede estar vacio"
    return errors


def validate_weight_percentage(value):
    if value is not None and (value <= 0 or value > 100):
        return {"weight_percentage": "El peso debe estar entre 1 y 100"}
    return {}


def validate_max_score(value):
    if value is not None and value <= 0:
        return {"max_score": "La puntuacion maxima debe ser positiva"}
    return {}


def validate_due_date_within_period(due_date, academic_period):
    if not due_date or not academic_period:
        return {}
    if isinstance(due_date, str):
        try:
            due_date = date.fromisoformat(due_date)
        except ValueError:
            return {"due_date": "Formato de fecha inválido. Use YYYY-MM-DD"}
    if due_date < academic_period.start_date or due_date > academic_period.end_date:
        return {
            "due_date": (
                f"La fecha debe estar dentro del período académico "
                f"({academic_period.start_date} - {academic_period.end_date})"
            )
        }
    return {}


def validate_period_not_locked(academic_period, field="due_date"):
    if academic_period and getattr(academic_period, "grades_locked", False):
        return {
            field: "El período académico está cerrado para calificaciones y actividades evaluativas"
        }
    return {}


def run_all_validators(**kwargs):
    errors = {}
    errors.update(
        validate_required_fields(
            kwargs,
            [
                "block_component_id",
                "teacher_subject_section_id",
                "title",
                "max_score",
                "due_date",
            ],
        )
    )
    errors.update(validate_max_score(kwargs.get("max_score")))
    academic_period = kwargs.get("academic_period")
    if academic_period:
        errors.update(validate_period_not_locked(academic_period))
        errors.update(
            validate_due_date_within_period(kwargs.get("due_date"), academic_period)
        )
    return errors


def run_activity_update_validators(**kwargs):
    """Validaciones para actualización de actividad evaluativa."""
    errors = {}
    academic_period = kwargs.get("academic_period")
    due_date = kwargs.get("due_date")
    if academic_period:
        errors.update(validate_period_not_locked(academic_period))
        if due_date is not None:
            errors.update(validate_due_date_within_period(due_date, academic_period))
    return errors
