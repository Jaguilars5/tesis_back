from apps.core.repositories.base import BaseRepository
from apps.attendance.models.incident_type import IncidentType


class IncidentTypeRepository(BaseRepository):
    model = IncidentType
