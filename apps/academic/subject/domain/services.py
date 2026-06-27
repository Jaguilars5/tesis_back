from django.db import transaction

from ..application import validators
from ..infrastructure.repositories import SubjectRepository


class SubjectService:
    repository = SubjectRepository

    @classmethod
    def _validate_or_raise(cls, **kwargs):
        errors = validators.run_all_validators(**kwargs)
        if errors:
            raise ValueError(errors)

    @classmethod
    @transaction.atomic
    def create_subject(cls, name, code):
        cls._validate_or_raise(name=name, code=code)
        existing = cls.repository.first(code=code)
        if existing:
            raise ValueError({"code": "Ya existe una materia con este codigo"})
        return cls.repository.create(name=name, code=code)

    @classmethod
    def get_subject(cls, subject_id):
        subject = cls.repository.get_by_id(subject_id)
        if not subject:
            raise ValueError({"id": f"Materia {subject_id} no encontrada"})
        return subject

    @classmethod
    @transaction.atomic
    def update_subject(cls, subject_id, **kwargs):
        allowed = {"name", "code", "is_active"}
        subject = cls.get_subject(subject_id)
        cls._validate_or_raise(
            name=kwargs.get("name", subject.name),
            code=kwargs.get("code", subject.code),
        )
        if "code" in kwargs:
            existing = cls.repository.first(code=kwargs["code"])
            if existing and existing.id != subject_id:
                raise ValueError({"code": "Ya existe otra materia con este codigo"})
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(subject.id, **clean)

    @classmethod
    @transaction.atomic
    def soft_delete(cls, pk, confirm=False):
        obj = cls.get_subject(pk)
        counts = cls.repository.get_cascade_counts(pk)
        total = sum(counts.values())

        if total > 0 and not confirm:
            parts = [f"{v} {k}" for k, v in counts.items()]
            return {
                "requires_confirmation": True,
                "affected_records": total,
                "message": f"Esta accion desactivar\u00e1 {', '.join(parts)} relacionados",
                "id": obj.id,
                "is_active": True,
            }

        total = cls.repository.deactivate_cascade(pk)
        return {
            "id": obj.id,
            "is_active": False,
            "deactivated_records": total,
        }
