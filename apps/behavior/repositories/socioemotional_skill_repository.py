from apps.core.repositories.base import BaseRepository
from apps.behavior.models.socioemotional_skill import SocioemotionalSkill


class SocioemotionalSkillRepository(BaseRepository):
    model = SocioemotionalSkill
