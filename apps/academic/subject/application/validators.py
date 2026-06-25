"""
Validaciones de negocio para Subject.

Cada funci\u00f3n validadora recibe los datos necesarios y retorna un dict
{field: mensaje} si la regla se viola, o un dict vacio si pasa.

Las funciones son PURAS: no mutan estado, no escriben a la DB.
El service las orquesta y acumula los errores.
"""


def validate_required_fields(**kwargs):
    errors = {}
    for field in ["name", "code"]:
        value = kwargs.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors[field] = f"{field} es obligatorio"
    return errors


def validate_code_format(code):
    if code and not code.strip():
        return {"code": "El c\u00f3digo no puede estar vac\u00edo"}
    return {}


def run_all_validators(**kwargs):
    errors = {}
    errors.update(validate_required_fields(**kwargs))
    errors.update(validate_code_format(kwargs.get("code")))
    return errors
