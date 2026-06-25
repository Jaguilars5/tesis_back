"""
Validaciones de negocio para SubjectOffering.

Cada funci\u00f3n validadora recibe los datos necesarios y retorna un dict
{field: mensaje} si la regla se viola, o un dict vacio si pasa.

Las funciones son PURAS: no mutan estado, no escriben a la DB.
El service las orquesta y acumula los errores.
"""


def validate_required_fields(**kwargs):
    errors = {}
    for field in ["section_id", "subject_academic_config_id"]:
        if field in kwargs and kwargs[field] is None:
            errors[field] = f"{field} es obligatorio"
    return errors


def run_all_validators(**kwargs):
    errors = {}
    errors.update(validate_required_fields(**kwargs))
    return errors
