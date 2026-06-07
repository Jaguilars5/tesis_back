from apps.core.repositories.base import BaseRepository
from ..models import School_Year


class SchoolYearRepository(BaseRepository):
    model = School_Year
