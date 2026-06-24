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
