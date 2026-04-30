import django_filters
from ..models import Section, Subject, Student_Note

class SectionFilter(django_filters.FilterSet):
    class Meta:
        model = Section
        fields = ['school_year', 'level', 'grade']

class SubjectFilter(django_filters.FilterSet):
    class Meta:
        model = Subject
        fields = ['school_year', 'section', 'active']

class StudentNoteFilter(django_filters.FilterSet):
    class Meta:
        model = Student_Note
        fields = ['student', 'academic_activity', 'academic_period']
