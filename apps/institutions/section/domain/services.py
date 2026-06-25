from ..infrastructure.repositories import SectionRepository


class SectionService:
    repository = SectionRepository

    @classmethod
    def create_section(cls, **kwargs):
        return cls.repository.create(**kwargs)

    @classmethod
    def get_section(cls, pk):
        obj = cls.repository.get_by_id(pk)
        if not obj:
            raise ValueError(f"Secci\u00f3n {pk} no encontrada")
        return obj

    @classmethod
    def update_section(cls, pk, **kwargs):
        obj = cls.get_section(pk)
        allowed = {"school_year_id", "academic_grade_id", "code", "parallel", "capacity", "is_active"}
        clean = {k: v for k, v in kwargs.items() if k in allowed}
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
