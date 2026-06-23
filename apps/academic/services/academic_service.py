from django.db.models import Q
from ..models import (
    Subject,
    AcademicPeriod,
    TeacherSubjectSection,
    SubjectAcademicConfig,
    SubjectOffering,
    PeriodType,
    ClassSchedule,
)
from ..repositories.academic_repo import (
    SubjectRepository,
    AcademicPeriodRepository,
    PeriodTypeRepository,
    TeacherSubjectSectionRepository,
    SubjectAcademicConfigRepository,
    SubjectOfferingRepository,
)
from ..repositories.class_schedule_repo import ClassScheduleRepository
from .. import validators
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
        return SectionRepository.create(
            school_year_id=school_year_id,
            academic_grade_id=academic_grade_id,
            parallel=parallel,
            capacity=capacity,
        )

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
            "offerings": SubjectOfferingRepository.get_by_section(section.id),
            "teachers": TeacherSubjectSectionRepository.get_by_section(section.id),
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
        ALLOWED_FIELDS = {"parallel", "capacity", "academic_grade_id", "school_year_id"}
        section = AcademicService.get_section(section_id)
        if "capacity" in kwargs and kwargs["capacity"] <= 0:
            raise ValueError("Capacidad debe ser mayor a 0")
        clean = {k: v for k, v in kwargs.items() if k in ALLOWED_FIELDS}
        return SectionRepository.update(section.id, **clean)

    # =====================
    # SUBJECT METHODS
    # =====================

    @staticmethod
    def create_subject(name, code):
        return SubjectRepository.create(name=name, code=code)

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
            "configs": SubjectAcademicConfigRepository.get_by_subject(subject.id),
            "teachers": TeacherSubjectSectionRepository.get_by_subject(subject.id),
        }

    @staticmethod
    def list_subjects_by_section(section_id):
        return (
            SubjectRepository.model.objects.filter(
                Q(subjectacademicconfig__subjectoffering__section_id=section_id) &
                Q(is_active=True)
            )
            .distinct()
            .order_by("name")
        )

    @staticmethod
    def update_subject(subject_id, **kwargs):
        ALLOWED_FIELDS = {"name", "code", "is_active"}
        subject = AcademicService.get_subject(subject_id)
        clean = {k: v for k, v in kwargs.items() if k in ALLOWED_FIELDS}
        return SubjectRepository.update(subject.id, **clean)

    # =====================
    # ACADEMIC_PERIOD METHODS
    # =====================

    @staticmethod
    def _validate_or_raise(period_type_obj, school_year_id, start_date, end_date, year_weight, is_regular_period, exclude_period_id=None):
        """Acumula errores de los validadores y lanza ValueError(dict) si hay alguno."""
        from apps.institutions.models import SchoolYear
        school_year = SchoolYear.objects.filter(pk=school_year_id).first()
        if not school_year:
            raise ValueError({"school_year": f"Año escolar {school_year_id} no encontrado"})
        errors = validators.run_all_validators(
            school_year_id=school_year_id,
            period_type_obj=period_type_obj,
            start_date=start_date,
            end_date=end_date,
            year_weight=year_weight,
            is_regular_period=is_regular_period,
            exclude_period_id=exclude_period_id,
        )
        if errors:
            raise ValueError(errors)

    @staticmethod
    def create_academic_period(
        name,
        school_year_id,
        period_type="TRIMESTRE",
        start_date=None,
        end_date=None,
        is_regular_period=True,
        year_weight=None,
    ):
        if not start_date or not end_date:
            raise ValueError({"start_date": "Las fechas de inicio y fin son requeridas"})
        if start_date >= end_date:
            raise ValueError({"start_date": "La fecha de inicio debe ser anterior a la fecha de fin"})
        period_type_obj = (
            PeriodTypeRepository.get_by_code(period_type)
            if isinstance(period_type, str)
            else period_type
        )
        if not period_type_obj:
            raise ValueError({"period_type": f"Tipo de período '{period_type}' no encontrado"})

        AcademicService._validate_or_raise(
            period_type_obj=period_type_obj,
            school_year_id=school_year_id,
            start_date=start_date,
            end_date=end_date,
            year_weight=year_weight,
            is_regular_period=is_regular_period,
        )

        return AcademicPeriodRepository.create(
            school_year_id=school_year_id,
            name=name,
            period_type=period_type_obj,
            start_date=start_date,
            end_date=end_date,
            is_regular_period=is_regular_period,
            year_weight=year_weight,
        )

    @staticmethod
    def get_academic_period(period_id):
        period = AcademicPeriodRepository.get_by_id(period_id)
        if not period:
            raise ValueError({"id": f"Período académico {period_id} no encontrado"})
        return period

    @staticmethod
    def list_periods_by_school_year(school_year_id):
        return AcademicPeriodRepository.get_by_school_year(school_year_id)

    @staticmethod
    def update_academic_period(period_id, **kwargs):
        ALLOWED_FIELDS = {"name", "start_date", "end_date", "is_regular_period", "year_weight", "is_active"}
        period = AcademicService.get_academic_period(period_id)
        start = kwargs.get("start_date", period.start_date)
        end = kwargs.get("end_date", period.end_date)
        if start >= end:
            raise ValueError({"start_date": "La fecha de inicio debe ser anterior a la fecha de fin"})

        year_weight = kwargs.get("year_weight", period.year_weight)
        is_regular_period = kwargs.get("is_regular_period", period.is_regular_period)

        AcademicService._validate_or_raise(
            period_type_obj=period.period_type,
            school_year_id=period.school_year_id,
            start_date=start,
            end_date=end,
            year_weight=year_weight,
            is_regular_period=is_regular_period,
            exclude_period_id=period.id,
        )

        clean = {k: v for k, v in kwargs.items() if k in ALLOWED_FIELDS}
        return AcademicPeriodRepository.update(period.id, **clean)

    # =====================
    # TEACHER_SUBJECT_SECTION METHODS
    # =====================

    @staticmethod
    def assign_teacher(user_id, subject_offering_id):
        if TeacherSubjectSectionRepository.exists_by_user_and_offering(user_id, subject_offering_id):
            raise ValueError("Docente ya está asignado a esta oferta de materia")
        return TeacherSubjectSectionRepository.create(
            user_id=user_id,
            subject_offering_id=subject_offering_id,
        )

    @staticmethod
    def get_teacher_assignment(assignment_id):
        assignment = TeacherSubjectSectionRepository.get_by_id(assignment_id)
        if not assignment:
            raise ValueError(f"Asignación {assignment_id} no encontrada")
        return assignment

    @staticmethod
    def list_teacher_assignments(user_id=None, subject_offering_id=None):
        return TeacherSubjectSectionRepository.filter_by_assignments(
            user_id=user_id,
            subject_offering_id=subject_offering_id,
        )

    @staticmethod
    def remove_teacher_assignment(assignment_id):
        AcademicService.get_teacher_assignment(assignment_id)
        TeacherSubjectSectionRepository.delete(assignment_id)
        return True

    # =====================
    # CLASS SCHEDULE METHODS
    # =====================

    @staticmethod
    def create_schedule(teacher_subject_section_id, day_of_week, start_time, end_time):
        if start_time >= end_time:
            raise ValueError("La hora de inicio debe ser anterior a la hora de fin")
        if ClassScheduleRepository.check_overlap(
            teacher_subject_section_id, day_of_week, start_time, end_time
        ):
            raise ValueError("El horario se superpone con otro existente")
        return ClassScheduleRepository.create(
            teacher_subject_section_id=teacher_subject_section_id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
        )

    @staticmethod
    def get_schedule(schedule_id):
        schedule = ClassScheduleRepository.get_by_id(schedule_id)
        if not schedule:
            raise ValueError(f"Horario {schedule_id} no encontrado")
        return schedule

    @staticmethod
    def get_all_schedules():
        return ClassScheduleRepository.get_all()

    @staticmethod
    def get_schedules_by_offering(subject_offering_id):
        return ClassScheduleRepository.get_by_subject_offering(subject_offering_id)

    @staticmethod
    def get_schedules_by_teacher(user_id):
        return ClassScheduleRepository.get_by_teacher(user_id)

    @staticmethod
    def update_schedule(schedule_id, **kwargs):
        ALLOWED_FIELDS = {"day_of_week", "start_time", "end_time", "is_active", "teacher_subject_section_id"}
        schedule = AcademicService.get_schedule(schedule_id)
        day_of_week = kwargs.get("day_of_week", schedule.day_of_week)
        start_time = kwargs.get("start_time", schedule.start_time)
        end_time = kwargs.get("end_time", schedule.end_time)
        if start_time >= end_time:
            raise ValueError("La hora de inicio debe ser anterior a la hora de fin")
        if ClassScheduleRepository.check_overlap(
            schedule.teacher_subject_section_id,
            day_of_week,
            start_time,
            end_time,
            exclude_id=schedule.id,
        ):
            raise ValueError("El horario se superpone con otro existente")
        clean = {k: v for k, v in kwargs.items() if k in ALLOWED_FIELDS}
        return ClassScheduleRepository.update(schedule.id, **clean)

    @staticmethod
    def delete_schedule(schedule_id):
        AcademicService.get_schedule(schedule_id)
        ClassScheduleRepository.delete(schedule_id)
        return True
