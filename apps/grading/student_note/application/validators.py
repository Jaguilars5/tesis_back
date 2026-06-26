"""
Validaciones de negocio para StudentNote.
"""


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


def run_all_validators(**kwargs):
    errors = {}
    errors.update(validate_required_fields(kwargs, [
        "enrollment_id", "evaluative_activity_id",
    ]))
    errors.update(validate_numeric_score(kwargs.get("numeric_score")))
    return errors
