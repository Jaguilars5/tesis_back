"""
Validaciones de negocio para PeriodType.

Cada función validadora recibe los datos necesarios y retorna un dict
{field: mensaje} si la regla se viola, o un dict vacio si pasa.

Las funciones son PURAS: no mutan estado, no escriben a la DB.
El service las orquesta y acumula los errores.
"""


def validate_required_fields(**kwargs):
    errors = {}
    for field in ["code", "name"]:
        value = kwargs.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors[field] = f"{field} es obligatorio"
    return errors


def validate_code_format(code):
    if code and not code.strip():
        return {"code": "El codigo no puede estar vacio"}
    return {}


def validate_divisions_per_year(value):
    if value is not None and value < 1:
        return {"divisions_per_year": "Debe ser al menos 1"}
    return {}


def run_all_validators(**kwargs):
    errors = {}
    errors.update(validate_required_fields(**kwargs))
    errors.update(validate_code_format(kwargs.get("code")))
    errors.update(validate_divisions_per_year(kwargs.get("divisions_per_year")))
    return errors
