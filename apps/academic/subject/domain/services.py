from ..infrastructure.repositories import SubjectRepository


class SubjectService:
    repository = SubjectRepository

    @classmethod
    def create_subject(cls, name, code):
        existing = cls.repository.first(code=code)
        if existing:
            raise ValueError({"code": "Ya existe una materia con este código"})
        return cls.repository.create(name=name, code=code)

    @classmethod
    def get_subject(cls, subject_id):
        subject = cls.repository.get_by_id(subject_id)
        if not subject:
            raise ValueError({"id": f"Materia {subject_id} no encontrada"})
        return subject

    @classmethod
    def update_subject(cls, subject_id, **kwargs):
        allowed = {"name", "code", "is_active"}
        subject = cls.get_subject(subject_id)
        if "code" in kwargs:
            existing = cls.repository.first(code=kwargs["code"])
            if existing and existing.id != subject_id:
                raise ValueError({"code": "Ya existe otra materia con este código"})
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(subject.id, **clean)
