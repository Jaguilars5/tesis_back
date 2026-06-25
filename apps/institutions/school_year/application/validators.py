"""
Validaciones de negocio para SchoolYear.
"""

from django.utils import timezone


def validate_start_date_not_in_past(start_date):
    """Regla 1: La fecha de inicio no debe ser anterior a la fecha actual."""
    if start_date < timezone.localdate():
        return {"start_date": "La fecha de inicio no puede ser anterior a la fecha actual"}
    return {}


def validate_end_date_after_start_date(start_date, end_date):
    """Regla 2: La fecha de fin no debe ser menor que la fecha de inicio."""
    if end_date < start_date:
        return {"end_date": "La fecha de fin no puede ser menor que la fecha de inicio"}
    return {}


def run_all_validators(start_date, end_date):
    """Ejecuta todas las validaciones y retorna un diccionario de errores."""
    errors = {}
    errors.update(validate_start_date_not_in_past(start_date))
    errors.update(validate_end_date_after_start_date(start_date, end_date))
    return errors