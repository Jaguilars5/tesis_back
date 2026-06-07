from apps.core.repositories.base import BaseRepository
from apps.attendance.models.attendance_status import AttendanceStatus


class AttendanceStatusRepository(BaseRepository):
    model = AttendanceStatus
