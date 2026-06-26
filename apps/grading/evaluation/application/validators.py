"""
Validaciones de negocio para EvaluationBlock, BlockComponent y EvaluativeActivity.
"""


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
        return {"max_score": "La puntuaci\u00f3n m\u00e1xima debe ser positiva"}
    return {}


def run_all_validators(**kwargs):
    errors = {}
    errors.update(validate_required_fields(kwargs, [
        "block_component_id", "teacher_subject_section_id", "title", "max_score", "due_date",
    ]))
    errors.update(validate_max_score(kwargs.get("max_score")))
    return errors
