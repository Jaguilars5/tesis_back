"""
Validaciones de negocio para AcademicPeriod.

Cada función validadora recibe los datos necesarios y retorna un dict
{field: mensaje} si la regla se viola, o un dict vacio si pasa.

Las funciones son PURAS: no mutan estado, no escriben a la DB.
El service las orquesta y acumula los errores.
"""

from apps.academic.period_type.infrastructure.models import PeriodType
from apps.institutions.school_year import SchoolYear

from ..infrastructure.repositories import AcademicPeriodRepository


def validate_dates_within_school_year(school_year_id, start_date, end_date):
    """Regla 2: Las fechas del periodo deben caer dentro del anio escolar."""
    school_year = SchoolYear.objects.filter(pk=school_year_id).first()
    if not school_year:
        return {"school_year": f"Anio escolar {school_year_id} no encontrado"}
    if start_date < school_year.start_date or end_date > school_year.end_date:
        return {
            "school_year": (
                "Las fechas del periodo deben estar dentro del rango del anio "
                f"escolar ({school_year.start_date} - {school_year.end_date})"
            )
        }
    return {}


def validate_single_period_type_per_year(
    school_year_id, period_type_obj, exclude_period_id=None
):
    """Regla 5 (Ecuador): Un solo tipo de periodo por anio escolar."""
    existing_type_ids = AcademicPeriodRepository.get_period_types_in_school_year(
        school_year_id=school_year_id,
        exclude_period_id=exclude_period_id,
    )
    if existing_type_ids and period_type_obj.pk not in existing_type_ids:
        existing_type = PeriodType.objects.filter(pk__in=existing_type_ids).first()
        return {
            "period_type": (
                f"Este anio escolar ya utiliza el tipo de periodo '{existing_type.name}'. "
                f"No se puede mezclar con '{period_type_obj.name}'. "
                f"Estandar educativo Ecuador: un solo tipo de periodo por anio escolar."
            )
        }
    return {}


def validate_period_type_quota(school_year_id, period_type_obj, exclude_period_id=None):
    """Regla 1: No exceder divisions_per_year del tipo de periodo."""
    existing_count = AcademicPeriodRepository.count_by_school_year_and_period_type(
        school_year_id=school_year_id,
        period_type_id=period_type_obj.pk,
        exclude_period_id=exclude_period_id,
    )
    if existing_count >= period_type_obj.divisions_per_year:
        return {
            "period_type": (
                f"No se pueden crear mas periodos de tipo '{period_type_obj.name}' "
                f"en este anio escolar (maximo {period_type_obj.divisions_per_year}). "
                f"Ya existen {existing_count}."
            )
        }
    return {}


def validate_no_date_overlap(
    school_year_id, start_date, end_date, exclude_period_id=None
):
    """Regla 3: El rango de fechas no debe solaparse con otro periodo del mismo anio."""
    if AcademicPeriodRepository.has_overlapping_period(
        school_year_id=school_year_id,
        start_date=start_date,
        end_date=end_date,
        exclude_period_id=exclude_period_id,
    ):
        return {
            "start_date": (
                "El rango de fechas se superpone con otro periodo academico "
                "del mismo anio escolar"
            )
        }
    return {}


def validate_year_weight_sum(
    school_year_id,
    period_type_obj,
    year_weight,
    is_regular_period,
    exclude_period_id=None,
):
    """Regla 4: La suma de year_weight de periodos regulares no debe exceder 100%."""
    if not is_regular_period or year_weight is None:
        return {}
    current_sum = (
        AcademicPeriodRepository.sum_year_weight_by_school_year_and_period_type(
            school_year_id=school_year_id,
            period_type_id=period_type_obj.pk,
            exclude_period_id=exclude_period_id,
        )
    )
    new_total = current_sum + year_weight
    if new_total > 100:
        return {
            "year_weight": (
                f"La suma de year_weight de los periodos regulares de tipo "
                f"'{period_type_obj.name}' excede 100% (actual: {current_sum}, "
                f"intentando sumar: {year_weight})"
            )
        }
    return {}


def run_all_validators(
    school_year_id,
    period_type_obj,
    start_date,
    end_date,
    year_weight=None,
    is_regular_period=True,
    exclude_period_id=None,
):
    """
    Ejecuta todas las reglas y acumula los errores en un solo dict.
    Retorna dict[field, msg] con todos los errores detectados, o {} si todo pasa.
    """
    errors = {}
    errors.update(
        validate_dates_within_school_year(school_year_id, start_date, end_date)
    )
    if "school_year" in errors:
        return errors
    errors.update(
        validate_single_period_type_per_year(
            school_year_id, period_type_obj, exclude_period_id=exclude_period_id
        )
    )
    errors.update(
        validate_period_type_quota(
            school_year_id, period_type_obj, exclude_period_id=exclude_period_id
        )
    )
    errors.update(
        validate_no_date_overlap(
            school_year_id, start_date, end_date, exclude_period_id=exclude_period_id
        )
    )
    errors.update(
        validate_year_weight_sum(
            school_year_id,
            period_type_obj,
            year_weight,
            is_regular_period,
            exclude_period_id=exclude_period_id,
        )
    )
    return errors
