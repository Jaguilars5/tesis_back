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
            raise ValueError(f"Subnivel acad\u00e9mico {pk} no encontrado")
        return obj

    @classmethod
    def update_academic_sublevel(cls, pk, **kwargs):
        allowed = {"academic_level_id", "code", "name", "description", "is_active"}
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(pk, **clean)
