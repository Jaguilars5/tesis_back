from ..infrastructure.repositories import PeriodTypeRepository


class PeriodTypeService:
    repository = PeriodTypeRepository

    @classmethod
    def create_period_type(cls, code, name, description="", divisions_per_year=1):
        existing = cls.repository.first(code=code)
        if existing:
            raise ValueError({"code": "Ya existe un tipo de período con este código"})
        return cls.repository.create(
            code=code,
            name=name,
            description=description,
            divisions_per_year=divisions_per_year,
        )

    @classmethod
    def get_period_type(cls, period_type_id):
        obj = cls.repository.get_by_id(period_type_id)
        if not obj:
            raise ValueError({"id": f"Tipo de período {period_type_id} no encontrado"})
        return obj

    @classmethod
    def update_period_type(cls, period_type_id, **kwargs):
        allowed = {"code", "name", "description", "divisions_per_year", "is_active"}
        obj = cls.get_period_type(period_type_id)
        if "code" in kwargs:
            existing = cls.repository.first(code=kwargs["code"])
            if existing and existing.id != period_type_id:
                raise ValueError({"code": "Ya existe otro tipo de período con este código"})
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(obj.id, **clean)
