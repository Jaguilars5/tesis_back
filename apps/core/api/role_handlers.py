from django.db.models import QuerySet
from apps.iam import User
from apps.people.models import Person
from apps.students.models import Student, StudentRepresentative, Enrollment
from apps.academic.subject import Subject
from apps.academic.academic_period import AcademicPeriod
from apps.academic.subject_academic_config import SubjectAcademicConfig
from apps.academic.subject_offering import SubjectOffering
from apps.academic.teacher_subject_section import TeacherSubjectSection
from apps.grading.student_note import StudentNote, PeriodGradeSummary
from apps.grading.evaluation import EvaluationBlock, BlockComponent, EvaluativeActivity
from apps.attendance.attendance_core import Attendance
from apps.attendance.attendance_status import AttendanceStatus
from apps.behavior.conduct_incident import ConductIncident
from apps.behavior.behavior_evaluation import BehaviorEvaluation
from apps.behavior.incident_type import IncidentType
from apps.grading.qualitative_scale import QualitativeScale
from apps.analytics.early_alert.infrastructure.models import EarlyAlert
from apps.analytics.models import StudentRiskScore, StudentRiskFactor, StudentFeatureSnapshot, RiskFactor


class BaseRoleHandler:
    """
    Clase base abstracta para los manejadores de seguridad RLS basados en roles.
    Define la interfaz y las comprobaciones declarativas principales.
    """
    ALLOWED_MODELS = None
    DENIED_MODELS = None

    def __init__(self, user):
        self.user = user

    def filter(self, queryset) -> QuerySet:
        model = queryset.model

        # 1. Validación de guarda declarativa para modelos expresamente denegados
        if self.DENIED_MODELS is not None and model in self.DENIED_MODELS:
            return queryset.none()

        # 2. Validación de guarda declarativa para modelos permitidos
        if self.ALLOWED_MODELS is not None and model not in self.ALLOWED_MODELS:
            return queryset.none()

        return self._filter_logic(queryset)

    def _filter_logic(self, queryset) -> QuerySet:
        """
        Lógica específica de filtrado que debe ser implementada por cada subclase.
        """
        raise NotImplementedError("Los manejadores de rol concretos deben implementar _filter_logic")


class StudentRoleHandler(BaseRoleHandler):
    """
    Manejador para el rol de ESTUDIANTE.
    Solo permite el acceso a sus propios datos personales, académicos, de asistencia y de notas.
    """
    ALLOWED_MODELS = {
        User, Person, Student, Enrollment, TeacherSubjectSection,
        EvaluativeActivity, StudentNote, PeriodGradeSummary,
        Attendance, ConductIncident, BehaviorEvaluation,
    }
    DENIED_MODELS = {
        EarlyAlert, StudentRiskScore, StudentRiskFactor, StudentFeatureSnapshot
    }

    def _filter_logic(self, queryset) -> QuerySet:
        model = queryset.model

        # Datos Personales
        if model is User:
            return queryset.filter(id=self.user.id)
        elif model is Person:
            return queryset.filter(id=self.user.person.id)
        elif model is Student:
            return queryset.filter(person=self.user.person)

        # Datos Académicos y Secciones
        elif model is Enrollment:
            return queryset.filter(student__person=self.user.person)
        elif model is TeacherSubjectSection:
            return queryset.filter(
                subject_offering__section__enrollments__student__person=self.user.person
            ).distinct()
        elif model is EvaluativeActivity:
            return queryset.filter(
                teacher_subject_section__subject_offering__section__enrollments__student__person=self.user.person
            ).distinct()

        # Calificaciones y Notas
        elif model in (StudentNote, PeriodGradeSummary):
            return queryset.filter(enrollment__student__person=self.user.person).distinct()

        # Asistencia y Conducta
        elif model in (Attendance, ConductIncident, BehaviorEvaluation):
            return queryset.filter(enrollment__student__person=self.user.person).distinct()

        return queryset.none()


class RepresentativeRoleHandler(BaseRoleHandler):
    """
    Manejador para el rol de REPRESENTANTE.
    Permite acceso únicamente a los datos de sus estudiantes representados.
    """
    ALLOWED_MODELS = {
        User, Person, Student, StudentRepresentative, Enrollment,
        TeacherSubjectSection, EvaluativeActivity, StudentNote,
        PeriodGradeSummary, Attendance, ConductIncident,
        BehaviorEvaluation, EarlyAlert, StudentRiskScore,
        StudentRiskFactor
    }

    def _filter_logic(self, queryset) -> QuerySet:
        model = queryset.model

        # Datos Personales
        if model is User:
            return queryset.filter(id=self.user.id)
        elif model is Person:
            return queryset.filter(id=self.user.person.id)
        elif model is Student:
            return queryset.filter(representatives_set__person=self.user.person).distinct()
        elif model is StudentRepresentative:
            return queryset.filter(person=self.user.person)

        # Académicos
        elif model is Enrollment:
            return queryset.filter(
                student__representatives_set__person=self.user.person
            ).distinct()
        elif model is TeacherSubjectSection:
            return queryset.filter(
                subject_offering__section__enrollments__student__representatives_set__person=self.user.person
            ).distinct()
        elif model is EvaluativeActivity:
            return queryset.filter(
                teacher_subject_section__subject_offering__section__enrollments__student__representatives_set__person=self.user.person
            ).distinct()

        # Calificaciones y Notas
        elif model in (StudentNote, PeriodGradeSummary):
            return queryset.filter(
                enrollment__student__representatives_set__person=self.user.person
            ).distinct()

        # Asistencia, Conducta e Incidentes
        elif model in (Attendance, ConductIncident, BehaviorEvaluation):
            return queryset.filter(
                enrollment__student__representatives_set__person=self.user.person
            ).distinct()

        # Alertas Tempranas y Analítica Predictiva de sus representados
        elif model in (EarlyAlert, StudentRiskScore, StudentRiskFactor):
            return queryset.filter(student__representatives_set__person=self.user.person).distinct()

        return queryset.none()


class TeacherRoleHandler(BaseRoleHandler):
    """
    Manejador para el rol de DOCENTE.
    Permite acceso únicamente a los cursos, actividades, calificaciones, asistencia
    e incidentes de los estudiantes asignados a su carga horaria.
    """
    ALLOWED_MODELS = {
        User, Person, TeacherSubjectSection, EvaluativeActivity,
        StudentNote, PeriodGradeSummary,
        Attendance, ConductIncident, BehaviorEvaluation,
        EarlyAlert, StudentRiskScore, Enrollment
    }

    def filter(self, queryset) -> QuerySet:
        # Guarda crítica: Si el docente no tiene perfil físico de Person, se deniega todo acceso
        if not self.user.person:
            return queryset.none()
        return super().filter(queryset)

    def _filter_logic(self, queryset) -> QuerySet:
        model = queryset.model

        # Datos Personales
        if model is User:
            return queryset.filter(id=self.user.id)
        elif model is Person:
            return queryset.filter(id=self.user.person.id)

        # Cursos asignados
        elif model is TeacherSubjectSection:
            return queryset.filter(user=self.user)
        elif model is EvaluativeActivity:
            return queryset.filter(teacher_subject_section__user=self.user)

        # Calificaciones
        elif model == StudentNote:
            return queryset.filter(
                evaluative_activity__teacher_subject_section__user=self.user
            ).distinct()
        elif model is PeriodGradeSummary:
            return queryset.filter(
                enrollment__section__teacher_subject_sections__user=self.user
            ).distinct()

        # Asistencia y Comportamiento de sus alumnos en sus secciones
        elif model in (Attendance, ConductIncident, BehaviorEvaluation):
            return queryset.filter(teacher_subject_section__user=self.user).distinct()

        # Alertas Tempranas y Riesgo predictivo de alumnos bajo su asignación
        elif model in (EarlyAlert, StudentRiskScore):
            return queryset.filter(
                student__enrollments__section__teacher_subject_sections__user=self.user
            ).distinct()

        return queryset.none()


class CounselorRoleHandler(BaseRoleHandler):
    """
    Manejador para el rol de CONSEJERO.
    Permite acceso completo de lectura institucional a perfiles de estudiantes,
    representantes, comportamiento y alertas preventivas. No tienen acceso a calificaciones.
    """
    ALLOWED_MODELS = {
        Person, Student, StudentRepresentative, Enrollment,
        TeacherSubjectSection, EvaluativeActivity, ConductIncident,
        BehaviorEvaluation, EarlyAlert, StudentRiskScore,
        StudentRiskFactor, StudentFeatureSnapshot
    }

    def _filter_logic(self, queryset) -> QuerySet:
        # Para consejeros, los modelos en ALLOWED_MODELS no requieren filtrado de fila adicional
        # (acceso completo institucional permitido)
        return queryset


# Registry dict para el despacho dinámico de los manejadores por rol
ROLE_HANDLERS = {
    "ESTUDIANTE": StudentRoleHandler,
    "REPRESENTANTE": RepresentativeRoleHandler,
    "DOCENTE": TeacherRoleHandler,
    "CONSEJERO": CounselorRoleHandler,
}
