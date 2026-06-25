from django.db import transaction

from apps.academic.period_type.infrastructure.repositories import PeriodTypeRepository
from apps.institutions.school_year.infrastructure.repositories import SchoolYearRepository

from ..application import validators
from ..infrastructure.repositories import AcademicPeriodRepository


class AcademicPeriodService:
    repository = AcademicPeriodRepository

    @classmethod
    def _validate_or_raise(
        cls,
        period_type_obj,
        school_year_id,
        start_date,
        end_date,
        year_weight,
        is_regular_period,
        exclude_period_id=None,
    ):
        school_year = SchoolYearRepository.get_by_id(school_year_id)
        if not school_year:
            raise ValueError({"school_year": f"Año escolar {school_year_id} no encontrado"})
        errors = validators.run_all_validators(
            school_year_id=school_year_id,
            period_type_obj=period_type_obj,
            start_date=start_date,
            end_date=end_date,
            year_weight=year_weight,
            is_regular_period=is_regular_period,
            exclude_period_id=exclude_period_id,
        )
        if errors:
            raise ValueError(errors)

    @classmethod
    @transaction.atomic
    def create_academic_period(
        cls,
        name,
        school_year_id,
        period_type="TRIMESTRE",
        start_date=None,
        end_date=None,
        is_regular_period=True,
        year_weight=None,
    ):
        if not start_date or not end_date:
            raise ValueError({"start_date": "Las fechas de inicio y fin son requeridas"})
        if start_date >= end_date:
            raise ValueError({"start_date": "La fecha de inicio debe ser anterior a la fecha de fin"})

        period_type_obj = (
            PeriodTypeRepository.get_by_code(period_type)
            if isinstance(period_type, str)
            else period_type
        )
        if not period_type_obj:
            raise ValueError({"period_type": f"Tipo de período '{period_type}' no encontrado"})

        cls._validate_or_raise(
            period_type_obj=period_type_obj,
            school_year_id=school_year_id,
            start_date=start_date,
            end_date=end_date,
            year_weight=year_weight,
            is_regular_period=is_regular_period,
        )

        return cls.repository.create(
            school_year_id=school_year_id,
            name=name,
            period_type=period_type_obj,
            start_date=start_date,
            end_date=end_date,
            is_regular_period=is_regular_period,
            year_weight=year_weight,
        )

    @classmethod
    def get_academic_period(cls, period_id):
        period = cls.repository.get_by_id(period_id)
        if not period:
            raise ValueError(f"Período académico {period_id} no encontrado")
        return period

    @classmethod
    def list_periods_by_school_year(cls, school_year_id):
        return cls.repository.get_by_school_year(school_year_id)

    @classmethod
    @transaction.atomic
    def update_academic_period(cls, period_id, **kwargs):
        allowed_fields = {
            "name",
            "start_date",
            "end_date",
            "is_regular_period",
            "year_weight",
            "is_active",
            "period_type_id",
        }
        period = cls.get_academic_period(period_id)
        start = kwargs.get("start_date", period.start_date)
        end = kwargs.get("end_date", period.end_date)
        if start >= end:
            raise ValueError({"start_date": "La fecha de inicio debe ser anterior a la fecha de fin"})

        year_weight = kwargs.get("year_weight", period.year_weight)
        is_regular_period = kwargs.get("is_regular_period", period.is_regular_period)

        new_period_type_id = kwargs.pop("period_type_id", None)
        if new_period_type_id is not None:
            period_type_obj = PeriodTypeRepository.get_by_id(new_period_type_id)
            if not period_type_obj:
                raise ValueError({"period_type": f"Tipo de período {new_period_type_id} no encontrado"})
        else:
            period_type_obj = period.period_type

        cls._validate_or_raise(
            period_type_obj=period_type_obj,
            school_year_id=period.school_year_id,
            start_date=start,
            end_date=end,
            year_weight=year_weight,
            is_regular_period=is_regular_period,
            exclude_period_id=period.id,
        )

        clean = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if new_period_type_id is not None:
            clean["period_type_id"] = new_period_type_id
        return cls.repository.update(period.id, **clean)

    @classmethod
    @transaction.atomic
    def soft_delete(cls, pk, confirm=False):
        obj = cls.get_academic_period(pk)
        counts = cls.repository.get_cascade_counts(pk)
        total = sum(counts.values())

        if total > 0 and not confirm:
            parts = [f"{v} {k}" for k, v in counts.items()]
            return {
                "requires_confirmation": True,
                "affected_records": total,
                "message": f"Esta acción desactivará {', '.join(parts)} relacionados",
                "id": obj.id,
                "is_active": True,
            }

        total = cls.repository.deactivate_cascade(pk)
        return {
            "id": obj.id,
            "is_active": False,
            "deactivated_records": total,
        }
