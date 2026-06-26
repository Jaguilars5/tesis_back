"""
Validaciones de negocio para QualitativeScale.
"""


def validate_required_fields(data, required):
    errors = {}
    for field in required:
        if field not in data or data[field] is None:
            errors[field] = f"{field} es obligatorio"
        elif isinstance(data[field], str) and not data[field].strip():
            errors[field] = f"{field} no puede estar vacio"
    return errors


def validate_numeric_equivalence(value):
    if value is not None and (value <= 0 or value > 10):
        return {"numeric_equivalence": "La equivalencia numérica debe estar entre 0 y 10"}
    return {}


def run_all_validators(**kwargs):
    errors = {}
    errors.update(validate_required_fields(kwargs, ["code", "numeric_equivalence"]))
    errors.update(validate_numeric_equivalence(kwargs.get("numeric_equivalence")))
    return errors
