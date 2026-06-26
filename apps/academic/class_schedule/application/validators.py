"""
Validaciones de negocio para ClassSchedule.

Cada función validadora recibe los datos necesarios y retorna un dict
{field: mensaje} si la regla se viola, o un dict vacio si pasa.

Las funciones son PURAS: no mutan estado, no escriben a la DB.
El service las orquesta y acumula los errores.
"""


def validate_start_before_end(start_time, end_time):
    if start_time and end_time and start_time >= end_time:
        return {"start_time": "La hora de inicio debe ser anterior a la hora de fin"}
    return {}


def validate_day_of_week(day_of_week):
    if day_of_week is None or not (1 <= day_of_week <= 7):
        return {"day_of_week": "El dia de la semana debe estar entre 1 (Lunes) y 7 (Domingo)"}
    return {}


def validate_required_fields(**kwargs):
    errors = {}
    required = ["teacher_subject_section_id", "day_of_week", "start_time", "end_time"]
    for field in required:
        if field not in kwargs or kwargs[field] is None:
            errors[field] = f"{field} es obligatorio"
    return errors


def run_all_validators(**kwargs):
    errors = {}
    errors.update(validate_required_fields(**kwargs))
    errors.update(validate_day_of_week(kwargs.get("day_of_week")))
    errors.update(validate_start_before_end(kwargs.get("start_time"), kwargs.get("end_time")))
    return errors
