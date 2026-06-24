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
            raise ValueError(f"Nivel acad\u00e9mico {pk} no encontrado")
        return obj

    @classmethod
    def update_academic_level(cls, pk, **kwargs):
        allowed = {"name", "code", "is_active"}
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(pk, **clean)
