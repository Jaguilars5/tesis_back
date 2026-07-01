from ..application import validators
from ..infrastructure.repositories import SectionRepository


class SectionService:
    repository = SectionRepository

    @classmethod
    def create_section(cls, **kwargs):
        errors = validators.run_all_validators(**kwargs)
        code_errors = validators.validate_code_not_empty(kwargs.get("code", ""))
        if code_errors:
            errors.update(code_errors)
        cap_errors = validators.validate_capacity_required(kwargs.get("capacity"))
        if cap_errors:
            errors.update(cap_errors)
        sy_errors = validators.validate_school_year_required(kwargs.get("school_year"))
        if sy_errors:
            errors.update(sy_errors)
        ag_errors = validators.validate_academic_grade_required(kwargs.get("academic_grade"))
        if ag_errors:
            errors.update(ag_errors)
        if errors:
            raise ValueError(errors)
        return cls.repository.create(**kwargs)

    @classmethod
    def get_section(cls, pk):
        obj = cls.repository.get_by_id(pk)
        if not obj:
            raise ValueError(f"Sección {pk} no encontrada")
        return obj

    @classmethod
    def update_section(cls, pk, **kwargs):
        cls.get_section(pk)
        allowed = {"school_year_id", "academic_grade_id", "code", "parallel", "capacity", "is_active"}
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        errors = validators.run_all_validators(**clean)
        if errors:
            raise ValueError(errors)
        return cls.repository.update(pk, **clean)

    @classmethod
    def soft_delete(cls, pk, confirm=False):
        obj = cls.get_section(pk)
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
