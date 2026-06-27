"""
Validaciones de negocio para TeacherSubjectSection.

Cada funcion validadora recibe los datos necesarios y retorna un dict
{field: mensaje} si la regla se viola, o un dict vacio si pasa.
"""


def validate_required_fields(**kwargs):
    errors = {}
    for field in ["user_id", "subject_offering_id"]:
        if field in kwargs and kwargs[field] is None:
            errors[field] = f"{field} es obligatorio"
    return errors


def run_all_validators(**kwargs):
    errors = {}
    errors.update(validate_required_fields(**kwargs))
    return errors
