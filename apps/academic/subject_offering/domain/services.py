from ..infrastructure.repositories import SubjectOfferingRepository


class SubjectOfferingService:
    repository = SubjectOfferingRepository

    @classmethod
    def create_offering(cls, section_id, subject_academic_config_id):
        existing = cls.repository.exists(
            section_id=section_id,
            subject_academic_config_id=subject_academic_config_id,
        )
        if existing:
            raise ValueError({
                "non_field_errors": "Ya existe esta oferta de materia para la sección"
            })
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
    def update_offering(cls, offering_id, **kwargs):
        allowed = {"section_id", "subject_academic_config_id", "is_active"}
        cls.get_offering(offering_id)
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(offering_id, **clean)

    @classmethod
    def get_by_section(cls, section_id, school_year_id=None):
        return cls.repository.get_by_section(section_id, school_year_id=school_year_id)

    @classmethod
    def get_by_school_year(cls, school_year_id):
        return cls.repository.get_by_school_year(school_year_id)
