from ..infrastructure.repositories import AcademicSublevelRepository


class AcademicSublevelService:
    repository = AcademicSublevelRepository

    @classmethod
    def create_academic_sublevel(cls, academic_level_id, code, name, description=""):
        return cls.repository.create(
            academic_level_id=academic_level_id,
            code=code,
            name=name,
            description=description,
        )

    @classmethod
    def get_academic_sublevel(cls, pk):
        obj = cls.repository.get_by_id(pk)
        if not obj:
            raise ValueError(f"Subnivel academico {pk} no encontrado")
        return obj

    @classmethod
    def update_academic_sublevel(cls, pk, **kwargs):
        allowed = {"academic_level_id", "code", "name", "description", "is_active"}
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(pk, **clean)

    @classmethod
    def soft_delete(cls, pk, confirm=False):
        obj = cls.get_academic_sublevel(pk)
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
