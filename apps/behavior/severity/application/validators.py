"""
Validaciones de negocio para Severity.
"""


def validate_required_fields(data, required):
    errors = {}
    for field in required:
        if field not in data or data[field] is None:
            errors[field] = f"{field} es obligatorio"
        elif isinstance(data[field], str) and not data[field].strip():
            errors[field] = f"{field} no puede estar vacío"
    return errors


def validate_code_format(value):
    if value and len(value) > 20:
        return {"code": "El código no puede exceder 20 caracteres"}
    return {}


def run_all_validators(**kwargs):
    errors = {}
    errors.update(validate_required_fields(kwargs, ["code", "name"]))
    errors.update(validate_code_format(kwargs.get("code")))
    return errors
