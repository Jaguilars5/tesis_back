from django.db import transaction

from ..application import validators
from ..infrastructure.repositories import SubjectOfferingRepository


class SubjectOfferingService:
    repository = SubjectOfferingRepository

    @classmethod
    def _validate_or_raise(cls, **kwargs):
        errors = validators.run_all_validators(**kwargs)
        if errors:
            raise ValueError(errors)

    @classmethod
    @transaction.atomic
    def create_offering(cls, section_id, subject_academic_config_id):
        cls._validate_or_raise(
            section_id=section_id,
            subject_academic_config_id=subject_academic_config_id,
        )
        existing = cls.repository.exists(
            section_id=section_id,
            subject_academic_config_id=subject_academic_config_id,
        )
        if existing:
            raise ValueError(
                {"non_field_errors": "Ya existe esta oferta de materia para la seccion"}
            )
        return cls.repository.create(
            section_id=section_id,
            subject_academic_config_id=subject_academic_config_id,
        )

    @classmethod
    def get_offering(cls, offering_id):
        obj = cls.repository.get_by_id(offering_id)
        if not obj:
            raise ValueError({"id": f"Oferta de materia {offering_id} no encontrada"})
        return obj

    @classmethod
    @transaction.atomic
    def update_offering(cls, offering_id, **kwargs):
        allowed = {"section_id", "subject_academic_config_id", "is_active"}
        offering = cls.get_offering(offering_id)
        cls._validate_or_raise(**kwargs)

        new_section_id = kwargs.get("section_id", offering.section_id)
        new_config_id = kwargs.get(
            "subject_academic_config_id", offering.subject_academic_config_id
        )
        if (
            new_section_id != offering.section_id
            or new_config_id != offering.subject_academic_config_id
        ):
            duplicate = cls.repository.first(
                section_id=new_section_id,
                subject_academic_config_id=new_config_id,
            )
            if duplicate and duplicate.id != offering_id:
                raise ValueError(
                    {
                        "non_field_errors": "Ya existe esta oferta de materia para la seccion"
                    }
                )

        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(offering_id, **clean)

    @classmethod
    @transaction.atomic
    def soft_delete(cls, pk, confirm=False):
        obj = cls.get_offering(pk)
        counts = cls.repository.get_cascade_counts(pk)
        total = sum(counts.values())

        if total > 0 and not confirm:
            parts = [f"{v} {k}" for k, v in counts.items()]
            return {
                "requires_confirmation": True,
                "affected_records": total,
                "message": f"Esta accion desactivara {', '.join(parts)} relacionados",
                "id": obj.id,
                "is_active": True,
            }

        total = cls.repository.deactivate_cascade(pk)
        return {
            "id": obj.id,
            "is_active": False,
            "deactivated_records": total,
        }

    @classmethod
    def get_by_section(cls, section_id, school_year_id=None):
        return cls.repository.get_by_section(section_id, school_year_id=school_year_id)

    @classmethod
    def get_by_school_year(cls, school_year_id):
        return cls.repository.get_by_school_year(school_year_id)
