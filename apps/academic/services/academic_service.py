from decimal import Decimal
from django.db import transaction, models
from ..models import (
    Section,
    Subject,
    Config_Academic,
    Academic_Period,
    Academic_Activity,
    Timing_Regime,
    Teacher_Subject_Section,
    SubjectAcademicConfig,
    SubjectOffering,
)
from apps.grading.models import StudentNote
from ..repositories.academic_repo import (
    SectionRepository,
    SubjectRepository,
    AcademicPeriodRepository,
    TimingRegimeRepository,
    TeacherSubjectSectionRepository,
)
from apps.grading.repositories.grading_repo import StudentNoteRepository


class AcademicService:
    """Lógica de negocio para infraestructura académica"""

    # =====================
    # CONFIG_ACADEMIC METHODS
    # =====================

    @staticmethod
    def create_config_academic(
        school_year_id,
        institution_id,
        academic_period_type,
        number_of_periods,
        description="",
    ):
        """Crear configuración académica"""
        config = Config_Academic(
            school_year_id=school_year_id,
            institution_id=institution_id,
            academic_period_type=academic_period_type,
            number_of_periods=number_of_periods,
            description=description,
        )
        config.save()
        return config

    @staticmethod
    def get_config_academic(config_id):
        """Obtener configuración académica"""
        config = ConfigAcademicRepository.get_by_id(config_id)
        if not config:
            raise ValueError(f"Configuración académica {config_id} no encontrada")
        return config

    @staticmethod
    def list_configs(school_year_id=None):
        """Listar configuraciones académicas"""
        if school_year_id:
            return Config_Academic.objects.filter(school_year_id=school_year_id)
        return ConfigAcademicRepository.get_all()

    @staticmethod
    def update_config_academic(config_id, **kwargs):
        """Actualizar configuración académica"""
        config = AcademicService.get_config_academic(config_id)
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        config.save()
        return config

    # =====================
    # TIMING_REGIME METHODS
    # =====================

    @staticmethod
    def create_timing_regime(institution_id, name, description=""):
        """Crear régimen horario"""
        regime = Timing_Regime(
            institution_id=institution_id, name=name, description=description
        )
        regime.save()
        return regime

    @staticmethod
    def get_timing_regime(regime_id):
        """Obtener régimen horario"""
        regime = TimingRegimeRepository.get_by_id(regime_id)
        if not regime:
            raise ValueError(f"Régimen horario {regime_id} no encontrado")
        return regime

    @staticmethod
    def list_timing_regimes(institution_id=None):
        """Listar regímenes horarios"""
        if institution_id:
            return Timing_Regime.objects.filter(institution_id=institution_id)
        return TimingRegimeRepository.get_all()

    @staticmethod
    def update_timing_regime(regime_id, **kwargs):
        """Actualizar régimen horario"""
        regime = AcademicService.get_timing_regime(regime_id)
        for key, value in kwargs.items():
            if hasattr(regime, key):
                setattr(regime, key, value)
        regime.save()
        return regime

    # =====================
    # SECTION METHODS
    # =====================

    @staticmethod
    def create_section(
        school_year_id, timing_regime_id, academic_grade_id, parallel, capacity
    ):
        """Crear sección (grado/paralelo)"""
        if capacity <= 0:
            raise ValueError("Capacidad debe ser mayor a 0")

        section = Section(
            school_year_id=school_year_id,
            timing_regime_id=timing_regime_id,
            academic_grade_id=academic_grade_id,
            parallel=parallel,
            capacity=capacity,
        )
        section.save()
        return section

    @staticmethod
    def get_section(section_id):
        """Obtener sección"""
        section = SectionRepository.get_by_id(section_id)
        if not section:
            raise ValueError(f"Sección {section_id} no encontrada")
        return section

    @staticmethod
    def get_all_sections():
        """Listar todas las secciones"""
        return SectionRepository.get_all()

    @staticmethod
    def get_section_details(section_id):
        """Obtener detalles completos de sección"""
        section = AcademicService.get_section(section_id)
        return {
            "section": section,
            "offerings": SubjectOffering.objects.filter(section=section),
            "teachers": Teacher_Subject_Section.objects.filter(section=section),
            "student_count": (
                section.student_enrollment.count()
                if hasattr(section, "student_enrollment")
                else 0
            ),
        }

    @staticmethod
    def list_sections_by_school_year(school_year_id):
        """Listar secciones de un año escolar"""
        return Section.objects.filter(school_year_id=school_year_id).order_by(
            "academic_grade__sequence_order", "parallel"
        )

    @staticmethod
    def update_section(section_id, **kwargs):
        """Actualizar sección"""
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
        """Crear asignatura"""
        subject = Subject(name=name, code=code)
        subject.save()
        return subject

    @staticmethod
    def get_subject(subject_id):
        """Obtener asignatura"""
        subject = SubjectRepository.get_by_id(subject_id)
        if not subject:
            raise ValueError(f"Asignatura {subject_id} no encontrada")
        return subject

    @staticmethod
    def get_all_subjects():
        """Listar todas las asignaturas"""
        return SubjectRepository.get_all()

    @staticmethod
    def get_subject_details(subject_id):
        """Obtener detalles completos de asignatura"""
        subject = AcademicService.get_subject(subject_id)
        return {
            "subject": subject,
            "configs": SubjectAcademicConfig.objects.filter(subject=subject),
            "teachers": Teacher_Subject_Section.objects.filter(subject=subject),
            "activities": Academic_Activity.objects.filter(subject=subject),
        }

    @staticmethod
    def list_subjects_by_section(section_id):
        """Listar asignaturas de una sección"""
        return Subject.objects.filter(
            subjectacademicconfig__subjectoffering__section_id=section_id
        ).distinct().order_by("name")

    @staticmethod
    def update_subject(subject_id, **kwargs):
        """Actualizar asignatura"""
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
    def create_academic_period(config_academic_id, name, number, description=""):
        """Crear período académico"""
        period = Academic_Period(
            config_academic_id=config_academic_id,
            name=name,
            number=number,
            description=description,
        )
        period.save()
        return period

    @staticmethod
    def get_academic_period(period_id):
        """Obtener período académico"""
        period = AcademicPeriodRepository.get_by_id(period_id)
        if not period:
            raise ValueError(f"Período académico {period_id} no encontrado")
        return period

    @staticmethod
    def list_periods_by_config(config_id):
        """Listar períodos de una configuración"""
        return Academic_Period.objects.filter(config_academic_id=config_id).order_by(
            "number"
        )

    @staticmethod
    def update_academic_period(period_id, **kwargs):
        """Actualizar período académico"""
        period = AcademicService.get_academic_period(period_id)
        for key, value in kwargs.items():
            if hasattr(period, key):
                setattr(period, key, value)
        period.save()
        return period

    # =====================
    # ACADEMIC_ACTIVITY METHODS
    # =====================

    @staticmethod
    def create_academic_activity(
        config_academic_id,
        subject_id,
        name,
        value_max,
        weight,
        applies_to,
        is_recoverable=False,
        order=0,
    ):
        """Crear actividad evaluativa"""
        if value_max <= 0:
            raise ValueError("Calificación máxima debe ser mayor a 0")
        if weight < 0 or weight > 1:
            raise ValueError("Peso debe estar entre 0 y 1")

        # Obtener la asignatura
        subject = SubjectRepository.get_by_id(subject_id)
        if not subject:
            raise ValueError(f"Asignatura {subject_id} no encontrada")

        activity = Academic_Activity(
            config_academic_id=config_academic_id,
            subject=subject,
            name=name,
            value_max=value_max,
            weight=weight,
            applies_to=applies_to,
            is_recoverable=is_recoverable,
            order=order,
        )
        activity.save()
        return activity

    @staticmethod
    def get_academic_activity(activity_id):
        """Obtener actividad evaluativa"""
        activity = AcademicActivityRepository.get_by_id(activity_id)
        if not activity:
            raise ValueError(f"Actividad {activity_id} no encontrada")
        return activity

    @staticmethod
    def list_activities_by_subject(subject_id):
        """Listar actividades de una asignatura"""
        return Academic_Activity.objects.filter(subject_id=subject_id).order_by("order")

    @staticmethod
    def update_academic_activity(activity_id, **kwargs):
        """Actualizar actividad evaluativa"""
        activity = AcademicService.get_academic_activity(activity_id)

        if "value_max" in kwargs and kwargs["value_max"] <= 0:
            raise ValueError("Calificación máxima debe ser mayor a 0")
        if "weight" in kwargs and (kwargs["weight"] < 0 or kwargs["weight"] > 1):
            raise ValueError("Peso debe estar entre 0 y 1")

        for key, value in kwargs.items():
            if hasattr(activity, key):
                setattr(activity, key, value)

        activity.save()
        return activity

    # =====================
    # TEACHER_SUBJECT_SECTION METHODS
    # =====================

    @staticmethod
    def assign_teacher(user_id, subject_id, section_id, school_year_id):
        """Asignar docente a asignatura y sección"""
        # Validar que no exista asignación duplicada
        existing = Teacher_Subject_Section.objects.filter(
            user_id=user_id,
            subject_id=subject_id,
            section_id=section_id,
            school_year_id=school_year_id,
        ).exists()

        if existing:
            raise ValueError("Docente ya está asignado a esta asignatura-sección")

        assignment = Teacher_Subject_Section(
            user_id=user_id,
            subject_id=subject_id,
            section_id=section_id,
            school_year_id=school_year_id,
        )
        assignment.save()
        return assignment

    @staticmethod
    def get_teacher_assignment(assignment_id):
        """Obtener asignación de docente"""
        assignment = TeacherSubjectSectionRepository.get_by_id(assignment_id)
        if not assignment:
            raise ValueError(f"Asignación {assignment_id} no encontrada")
        return assignment

    @staticmethod
    def list_teacher_assignments(user_id=None, subject_id=None, section_id=None):
        """Listar asignaciones con filtros"""
        query = Teacher_Subject_Section.objects.all()

        if user_id:
            query = query.filter(user_id=user_id)
        if subject_id:
            query = query.filter(subject_id=subject_id)
        if section_id:
            query = query.filter(section_id=section_id)

        return query

    @staticmethod
    def remove_teacher_assignment(assignment_id):
        """Eliminar asignación de docente"""
        assignment = AcademicService.get_teacher_assignment(assignment_id)
        assignment.delete()
        return True

    # =====================
    # STUDENT_NOTE METHODS
    # =====================

    @staticmethod
    def record_student_note(
        student_id,
        academic_activity_id,
        academic_period_id,
        teacher_subject_section_id,
        note_value,
        observation="",
        device_origin=None,
    ):
        """Registrar calificación de estudiante"""
        # Validar que nota esté en rango válido
        activity = Academic_Activity.objects.get(id=academic_activity_id)
        if note_value < 0 or note_value > activity.value_max:
            raise ValueError(f"Nota debe estar entre 0 y {activity.value_max}")

        # Calcular nota normalizada (ej: de 20 a 10)
        normalized = (note_value / activity.value_max) * 10
        normalized = Decimal(normalized).quantize(Decimal("0.01"))

        # Evitar duplicados
        existing = StudentNote.objects.filter(
            student_id=student_id,
            academic_activity_id=academic_activity_id,
            academic_period_id=academic_period_id,
            teacher_subject_section_id=teacher_subject_section_id,
        ).first()

        if existing:
            existing.note_value = note_value
            existing.normalized_value = normalized
            existing.observation = observation
            existing.sync_status = "pending"
            existing.save()
            return existing

        note = StudentNote(
            student_id=student_id,
            academic_activity_id=academic_activity_id,
            academic_period_id=academic_period_id,
            teacher_subject_section_id=teacher_subject_section_id,
            note_value=note_value,
            normalized_value=normalized,
            observation=observation,
            sync_status="pending",
            device_origin=device_origin,
        )
        note.save()
        return note

    @staticmethod
    def get_student_note(note_id):
        """Obtener calificación"""
        note = StudentNoteRepository.get_by_id(note_id)
        if not note:
            raise ValueError(f"Calificación {note_id} no encontrada")
        return note

    @staticmethod
    def list_student_notes(
        student_id=None, academic_period_id=None, subject_id=None, section_id=None
    ):
        """Listar calificaciones con filtros"""
        query = StudentNote.objects.filter(active=True)

        if student_id:
            query = query.filter(student_id=student_id)
        if academic_period_id:
            query = query.filter(academic_period_id=academic_period_id)
        if subject_id:
            query = query.filter(teacher_subject_section__subject_id=subject_id)
        if section_id:
            query = query.filter(teacher_subject_section__section_id=section_id)

        return query.order_by("-created_at")

    @staticmethod
    def calculate_period_average(student_id, subject_id, academic_period_id):
        """Calcular promedio del estudiante en una materia por período"""
        notes = StudentNote.objects.filter(
            student_id=student_id,
            academic_period_id=academic_period_id,
            teacher_subject_section__subject_id=subject_id,
            active=True,
        )

        if not notes.exists():
            return None

        # Promedio ponderado por peso de actividad
        total_weight = 0
        weighted_sum = Decimal(0)

        for note in notes:
            weight = note.academic_activity.weight
            weighted_sum += note.normalized_value * Decimal(weight)
            total_weight += weight

        if total_weight == 0:
            return None

        average = weighted_sum / Decimal(total_weight)
        return average.quantize(Decimal("0.01"))

    @staticmethod
    def calculate_section_average(section_id, subject_id, academic_period_id):
        """Calcular promedio de una sección en una materia"""
        notes = StudentNote.objects.filter(
            academic_period_id=academic_period_id,
            teacher_subject_section__subject_id=subject_id,
            teacher_subject_section__section_id=section_id,
            active=True,
        )

        if not notes.exists():
            return None

        avg = notes.aggregate(models.Avg("normalized_value"))["normalized_value__avg"]
        if avg is None:
            return None
        return Decimal(avg).quantize(Decimal("0.01"))

    @staticmethod
    def mark_notes_synced(note_ids):
        """Marcar notas como sincronizadas"""
        from django.utils import timezone
        import time

        StudentNote.objects.filter(id__in=note_ids).update(
            sync_status="synced",
            sync_timestamp=int(time.time() * 1000),
            sync_version=models.F("sync_version") + 1,
        )
        return True

    @staticmethod
    def deactivate_student_note(note_id):
        """Desactivar calificación (soft delete)"""
        note = AcademicService.get_student_note(note_id)
        note.active = False
        note.save()
        return note
