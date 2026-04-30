from ..models import (
    Section, Subject, Config_Academic, Academic_Period, 
    Academic_Activity, Timing_Regime, Teacher_Subject_Section
)

class BaseRepository:
    model = None

    @classmethod
    def get_all(cls, active_only=True):
        queryset = cls.model.objects.all()
        if active_only and hasattr(cls.model, 'active'):
            queryset = queryset.filter(active=True)
        return queryset

    @classmethod
    def get_by_id(cls, pk):
        try:
            return cls.model.objects.get(pk=pk)
        except cls.model.DoesNotExist:
            return None

class SectionRepository(BaseRepository):
    model = Section

class SubjectRepository(BaseRepository):
    model = Subject

class ConfigAcademicRepository(BaseRepository):
    model = Config_Academic

class AcademicPeriodRepository(BaseRepository):
    model = Academic_Period

class AcademicActivityRepository(BaseRepository):
    model = Academic_Activity

class TimingRegimeRepository(BaseRepository):
    model = Timing_Regime

class TeacherSubjectSectionRepository(BaseRepository):
    model = Teacher_Subject_Section

