from apps.core.repositories.base import BaseRepository
from apps.attendance.models.socioemotional_skill import SocioemotionalSkill


class SocioemotionalSkillRepository(BaseRepository):
    model = SocioemotionalSkill
