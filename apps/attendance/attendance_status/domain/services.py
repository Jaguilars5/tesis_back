from ..infrastructure.repositories import AttendanceStatusRepository


class AttendanceStatusService:
    """Lógica de negocio para estados de asistencia."""

    repository = AttendanceStatusRepository

    @classmethod
    def create_attendance_status(cls, code, name, description=""):
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
        allowed = {"code", "name", "description", "is_active"}
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(pk, **clean)
