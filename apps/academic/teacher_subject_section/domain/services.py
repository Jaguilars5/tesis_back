from django.db import transaction

from ..application import validators
from ..infrastructure.repositories import TeacherSubjectSectionRepository


class TeacherSubjectSectionService:
    repository = TeacherSubjectSectionRepository

    @classmethod
    def _validate_or_raise(cls, **kwargs):
        errors = validators.run_all_validators(**kwargs)
        if errors:
            raise ValueError(errors)

    @classmethod
    @transaction.atomic
    def assign_teacher(cls, user_id, subject_offering_id):
        cls._validate_or_raise(
            user_id=user_id,
            subject_offering_id=subject_offering_id,
        )
        if cls.repository.exists_by_user_and_offering(user_id, subject_offering_id):
            raise ValueError({
                "non_field_errors": "Docente ya est\u00e1 asignado a esta oferta de materia"
            })
        return cls.repository.create(
            user_id=user_id,
            subject_offering_id=subject_offering_id,
        )

    @classmethod
    def get_assignment(cls, assignment_id):
        assignment = cls.repository.get_by_id(assignment_id)
        if not assignment:
            raise ValueError({"id": f"Asignacion {assignment_id} no encontrada"})
        return assignment

    @classmethod
    @transaction.atomic
    def update_assignment(cls, assignment_id, **kwargs):
        allowed = {"is_active", "subject_offering_id"}
        cls.get_assignment(assignment_id)
        cls._validate_or_raise(**kwargs)
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(assignment_id, **clean)

    @classmethod
    def remove_assignment(cls, assignment_id):
        cls.get_assignment(assignment_id)
        cls.repository.delete(assignment_id)
        return True

    @classmethod
    @transaction.atomic
    def soft_delete(cls, pk, confirm=False):
        obj = cls.get_assignment(pk)
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

    @classmethod
    def list_assignments(cls, user_id=None, subject_offering_id=None):
        return cls.repository.filter_by_assignments(
            user_id=user_id,
            subject_offering_id=subject_offering_id,
        )
