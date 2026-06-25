"""
Validaciones de negocio para SubjectAcademicConfig.

Cada funci\u00f3n validadora recibe los datos necesarios y retorna un dict
{field: mensaje} si la regla se viola, o un dict vacio si pasa.

Las funciones son PURAS: no mutan estado, no escriben a la DB.
El service las orquesta y acumula los errores.
"""


def validate_required_fields(**kwargs):
    errors = {}
    checks = {"subject_id": kwargs.get("subject_id"), "academic_grade_id": kwargs.get("academic_grade_id")}
    for field, value in checks.items():
        if field in kwargs and value is None:
            errors[field] = f"{field} es obligatorio"
    if "weekly_hours" in kwargs and kwargs["weekly_hours"] is None:
        errors["weekly_hours"] = "weekly_hours es obligatorio"
    return errors


def validate_weekly_hours(value):
    if value is not None and value < 1:
        return {"weekly_hours": "Las horas semanales deben ser al menos 1"}
    return {}


def run_all_validators(**kwargs):
    errors = {}
    errors.update(validate_required_fields(**kwargs))
    errors.update(validate_weekly_hours(kwargs.get("weekly_hours")))
    return errors
