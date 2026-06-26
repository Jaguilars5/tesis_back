"""
Validaciones de negocio para BehaviorEvaluation.
"""


def validate_required_fields(data, required):
    errors = {}
    for field in required:
        if field not in data or data[field] is None:
            errors[field] = f"{field} es obligatorio"
    return errors


def run_all_validators(**kwargs):
    errors = {}
    errors.update(validate_required_fields(kwargs, [
        "enrollment_id", "academic_period_id",
    ]))
    return errors
