from decimal import Decimal
from django.db import transaction, models
from apps.institutions.models import Section
from ..models import (
    Subject,
    AcademicPeriod,
    TeacherSubjectSection,
    SubjectAcademicConfig,
    SubjectOffering,
    PeriodType,
)
from ..repositories.academic_repo import (
    SubjectRepository,
    AcademicPeriodRepository,
    TeacherSubjectSectionRepository,
)
from apps.institutions.repositories.section_repository import SectionRepository



class AcademicService:
    """Lógica de negocio para infraestructura académica"""

    # =====================
    # SECTION METHODS
    # =====================

    @staticmethod
    def create_section(school_year_id, academic_grade_id, parallel, capacity):
        if capacity <= 0:
            raise ValueError("Capacidad debe ser mayor a 0")
        section = Section(
            school_year_id=school_year_id,
            academic_grade_id=academic_grade_id,
            parallel=parallel,
            capacity=capacity,
        )
        section.save()
        return section

    @staticmethod
    def get_section(section_id):
        section = SectionRepository.get_by_id(section_id)
        if not section:
            raise ValueError(f"Sección {section_id} no encontrada")
        return section

    @staticmethod
    def get_all_sections():
        return SectionRepository.get_all()

    @staticmethod
    def get_section_details(section_id):
        section = AcademicService.get_section(section_id)
        return {
            "section": section,
            "offerings": SubjectOffering.objects.filter(section=section),
            "teachers": TeacherSubjectSection.objects.filter(section=section),
            "student_count": (
                section.student_enrollment.count()
                if hasattr(section, "student_enrollment")
                else 0
            ),
        }

    @staticmethod
    def list_sections_by_school_year(school_year_id):
        return SectionRepository.get_by_school_year(school_year_id)

    @staticmethod
    def update_section(section_id, **kwargs):
        section = AcademicService.get_section(section_id)
        if "capacity" in kwargs and kwargs["capacity"] <= 0:
            raise ValueError("Capacidad debe ser mayor a 0")
        for key, value in kwargs.items():
            if hasattr(section, key):
                setattr(section, key, value)
        section.save()
        return section

    # =====================
    # SUBJECT METHODS
    # =====================

    @staticmethod
    def create_subject(name, code):
        subject = Subject(name=name, code=code)
        subject.save()
        return subject

    @staticmethod
    def get_subject(subject_id):
        subject = SubjectRepository.get_by_id(subject_id)
        if not subject:
            raise ValueError(f"Asignatura {subject_id} no encontrada")
        return subject

    @staticmethod
    def get_all_subjects():
        return SubjectRepository.get_all()

    @staticmethod
    def get_subject_details(subject_id):
        subject = AcademicService.get_subject(subject_id)
        return {
            "subject": subject,
            "configs": SubjectAcademicConfig.objects.filter(subject=subject),
            "teachers": TeacherSubjectSection.objects.filter(subject=subject),
        }

    @staticmethod
    def list_subjects_by_section(section_id):
        return (
            Subject.objects.filter(
                subjectacademicconfig__subjectoffering__section_id=section_id
            )
            .distinct()
            .order_by("name")
        )

    @staticmethod
    def update_subject(subject_id, **kwargs):
        subject = AcademicService.get_subject(subject_id)
        for key, value in kwargs.items():
            if hasattr(subject, key):
                setattr(subject, key, value)
        subject.save()
        return subject

    # =====================
    # ACADEMIC_PERIOD METHODS
    # =====================

    @staticmethod
    def create_academic_period(name, school_year_id, period_type="REGULAR", start_date=None, end_date=None, is_regular_period=True):
        if not start_date or not end_date:
            raise ValueError("Las fechas de inicio y fin son requeridas")
        period_type_obj = PeriodType.objects.get(code=period_type) if isinstance(period_type, str) else period_type
        period = AcademicPeriod(
            school_year_id=school_year_id,
            name=name,
            period_type=period_type_obj,
            start_date=start_date,
            end_date=end_date,
            is_regular_period=is_regular_period,
        )
        period.save()
        return period

    @staticmethod
    def get_academic_period(period_id):
        period = AcademicPeriodRepository.get_by_id(period_id)
        if not period:
            raise ValueError(f"Período académico {period_id} no encontrado")
        return period

    @staticmethod
    def list_periods_by_school_year(school_year_id):
        return AcademicPeriod.objects.filter(school_year_id=school_year_id).order_by(
            "start_date"
        )

    @staticmethod
    def update_academic_period(period_id, **kwargs):
        period = AcademicService.get_academic_period(period_id)
        for key, value in kwargs.items():
            if hasattr(period, key):
                setattr(period, key, value)
        period.save()
        return period

    # =====================
    # TEACHER_SUBJECT_SECTION METHODS
    # =====================

    @staticmethod
    def assign_teacher(user_id, subject_offering_id):
        existing = TeacherSubjectSection.objects.filter(
            user_id=user_id,
            subject_offering_id=subject_offering_id,
        ).exists()
        if existing:
            raise ValueError("Docente ya está asignado a esta oferta de materia")
        assignment = TeacherSubjectSection(
            user_id=user_id,
            subject_offering_id=subject_offering_id,
        )
        assignment.save()
        return assignment

    @staticmethod
    def get_teacher_assignment(assignment_id):
        assignment = TeacherSubjectSectionRepository.get_by_id(assignment_id)
        if not assignment:
            raise ValueError(f"Asignación {assignment_id} no encontrada")
        return assignment

    @staticmethod
    def list_teacher_assignments(user_id=None, subject_offering_id=None):
        query = TeacherSubjectSection.objects.all()
        if user_id:
            query = query.filter(user_id=user_id)
        if subject_offering_id:
            query = query.filter(subject_offering_id=subject_offering_id)
        return query

    @staticmethod
    def remove_teacher_assignment(assignment_id):
        assignment = AcademicService.get_teacher_assignment(assignment_id)
        assignment.delete()
        return True
