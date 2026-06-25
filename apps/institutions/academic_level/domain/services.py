from ..infrastructure.repositories import AcademicLevelRepository


class AcademicLevelService:
    repository = AcademicLevelRepository

    @classmethod
    def create_academic_level(cls, name, code=""):
        return cls.repository.create(name=name, code=code)

    @classmethod
    def get_academic_level(cls, pk):
        obj = cls.repository.get_by_id(pk)
        if not obj:
            raise ValueError(f"Nivel academico {pk} no encontrado")
        return obj

    @classmethod
    def update_academic_level(cls, pk, **kwargs):
        allowed = {"name", "code", "is_active"}
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(pk, **clean)

    @classmethod
    def soft_delete(cls, pk, confirm=False):
        obj = cls.get_academic_level(pk)
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
