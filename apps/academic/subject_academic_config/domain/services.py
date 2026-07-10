from django.db import transaction

from ..application import validators
from ..infrastructure.repositories import SubjectAcademicConfigRepository


class SubjectAcademicConfigService:
    repository = SubjectAcademicConfigRepository

    @classmethod
    def _validate_or_raise(cls, **kwargs):
        errors = validators.run_all_validators(**kwargs)
        if errors:
            raise ValueError(errors)

    @classmethod
    @transaction.atomic
    def create_config(
        cls, subject_id, academic_grade_id, weekly_hours, is_required=True
    ):
        cls._validate_or_raise(
            subject_id=subject_id,
            academic_grade_id=academic_grade_id,
            weekly_hours=weekly_hours,
        )
        existing = cls.repository.exists(
            subject_id=subject_id,
            academic_grade_id=academic_grade_id,
        )
        if existing:
            raise ValueError(
                {
                    "non_field_errors": "Ya existe una configuracion para esta materia y grado"
                }
            )
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
            raise ValueError({"id": f"Configuracion {config_id} no encontrada"})
        return obj

    @classmethod
    @transaction.atomic
    def update_config(cls, config_id, **kwargs):
        allowed = {"weekly_hours", "is_required", "is_active"}
        cls.get_config(config_id)
        cls._validate_or_raise(**kwargs)
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(config_id, **clean)

    @classmethod
    @transaction.atomic
    def soft_delete(cls, pk, confirm=False):
        obj = cls.get_config(pk)
        counts = cls.repository.get_cascade_counts(pk)
        total = sum(counts.values())

        if total > 0 and not confirm:
            parts = [f"{v} {k}" for k, v in counts.items()]
            return {
                "requires_confirmation": True,
                "affected_records": total,
                "message": f"Esta accion desactivara {', '.join(parts)} relacionados",
                "id": obj.id,
                "is_active": True,
            }

        total = cls.repository.deactivate_cascade(pk)
        return {
            "id": obj.id,
            "is_active": False,
            "deactivated_records": total,
        }

    @classmethod
    def get_by_subject(cls, subject_id):
        return cls.repository.get_by_subject(subject_id)

    @classmethod
    def get_by_grade(cls, academic_grade_id):
        return cls.repository.get_by_grade(academic_grade_id)
