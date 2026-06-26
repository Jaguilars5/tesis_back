from ..application import validators
from ..infrastructure.repositories import AttendanceStatusRepository


class AttendanceStatusService:
    """Lógica de negocio para estados de asistencia."""

    repository = AttendanceStatusRepository

    @classmethod
    def create_attendance_status(cls, code, name, description=""):
        errors = validators.run_all_validators(code=code, name=name, description=description)
        if errors:
            raise ValueError(errors)
        return cls.repository.create(
            code=code,
            name=name,
            description=description,
        )

    @classmethod
    def get_attendance_status(cls, pk):
        obj = cls.repository.get_by_id(pk)
        if not obj:
            raise ValueError(f"Estado de asistencia {pk} no encontrado")
        return obj

    @classmethod
    def update_attendance_status(cls, pk, **kwargs):
        cls.get_attendance_status(pk)
        errors = validators.run_all_validators(**kwargs)
        if errors:
            raise ValueError(errors)
        allowed = {"code", "name", "description", "is_active"}
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(pk, **clean)

    @classmethod
    def soft_delete(cls, pk, confirm=False):
        obj = cls.get_attendance_status(pk)
        counts = cls.repository.get_cascade_counts(pk)
        total = sum(counts.values())

        if total > 0 and not confirm:
            parts = [f"{v} {k}" for k, v in counts.items()]
            return {
                "requires_confirmation": True,
                "affected_records": total,
                "message": f"Esta acción desactivará {', '.join(parts)} relacionados",
                "id": obj.id,
                "is_active": True,
            }

        total = cls.repository.deactivate_cascade(pk)
        return {
            "id": obj.id,
            "is_active": False,
            "deactivated_records": total,
        }
