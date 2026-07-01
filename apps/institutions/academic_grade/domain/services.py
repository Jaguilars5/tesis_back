from ..application import validators
from ..infrastructure.repositories import AcademicGradeRepository


class AcademicGradeService:
    repository = AcademicGradeRepository

    @classmethod
    def create_grade(cls, name, academic_sublevel_id, code=""):
        errors = validators.run_all_validators(name=name, code=code)
        sl_errors = validators.validate_academic_sublevel_required(academic_sublevel_id)
        if sl_errors:
            errors.update(sl_errors)
        if errors:
            raise ValueError(errors)
        return cls.repository.create(
            name=name,
            academic_sublevel_id=academic_sublevel_id,
            code=code,
        )

    @classmethod
    def get_grade(cls, grade_id):
        grade = cls.repository.get_by_id(grade_id)
        if not grade:
            raise ValueError(f"Grado {grade_id} no encontrado")
        return grade

    @classmethod
    def update_grade(cls, grade_id, **kwargs):
        allowed = {"name", "code", "academic_sublevel_id", "is_active"}
        cls.get_grade(grade_id)
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        errors = validators.run_all_validators(**clean)
        if errors:
            raise ValueError(errors)
        return cls.repository.update(grade_id, **clean)

    @classmethod
    def get_by_sublevel(cls, sublevel_id):
        return cls.repository.get_by_sublevel(sublevel_id)

    @classmethod
    def soft_delete(cls, pk, confirm=False):
        obj = cls.get_grade(pk)
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
