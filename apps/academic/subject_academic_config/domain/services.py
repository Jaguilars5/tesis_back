from ..infrastructure.repositories import SubjectAcademicConfigRepository


class SubjectAcademicConfigService:
    repository = SubjectAcademicConfigRepository

    @classmethod
    def create_config(cls, subject_id, academic_grade_id, weekly_hours, is_required=True):
        existing = cls.repository.exists(
            subject_id=subject_id,
            academic_grade_id=academic_grade_id,
        )
        if existing:
            raise ValueError({
                "non_field_errors": "Ya existe una configuración para esta materia y grado"
            })
        return cls.repository.create(
            subject_id=subject_id,
            academic_grade_id=academic_grade_id,
            weekly_hours=weekly_hours,
            is_required=is_required,
        )

    @classmethod
    def get_config(cls, config_id):
        obj = cls.repository.get_by_id(config_id)
        if not obj:
            raise ValueError({"id": f"Configuración {config_id} no encontrada"})
        return obj

    @classmethod
    def update_config(cls, config_id, **kwargs):
        allowed = {"weekly_hours", "is_required", "is_active"}
        cls.get_config(config_id)
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(config_id, **clean)

    @classmethod
    def get_by_subject(cls, subject_id):
        return cls.repository.get_by_subject(subject_id)

    @classmethod
    def get_by_grade(cls, academic_grade_id):
        return cls.repository.get_by_grade(academic_grade_id)
