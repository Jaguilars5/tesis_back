from rest_framework.filters import BaseFilterBackend

# Importar los modelos necesarios para la validación tipada de catálogos públicos
from apps.people.models import DocumentType
from apps.grading.qualitative_scale import QualitativeScale
from apps.attendance.attendance_status import AttendanceStatus
from apps.behavior.incident_type import IncidentType
from apps.institutions.school_year import SchoolYear
from apps.institutions.academic_level import AcademicLevel
from apps.institutions.academic_grade import AcademicGrade
from apps.institutions.section import Section
from apps.academic.academic_period import AcademicPeriod
from apps.academic.subject import Subject
from apps.academic.subject_academic_config import SubjectAcademicConfig
from apps.academic.subject_offering import SubjectOffering
from apps.analytics.student_risk import RiskFactor

from .role_handlers import ROLE_HANDLERS

PUBLIC_CATALOGS = {
    DocumentType,
    SchoolYear,
    AcademicPeriod,
    AcademicLevel,
    AcademicGrade,
    Subject,
    SubjectAcademicConfig,
    SubjectOffering,
    Section,
    QualitativeScale,
    AttendanceStatus,
    IncidentType,
    RiskFactor,
}


class RoleBasedFilterBackend(BaseFilterBackend):
    """
    Filtro global de seguridad a nivel de fila (Row-Level Security) en Django REST Framework.
    Garantiza que ningún usuario acceda a datos fuera de su ámbito relacional o rol institucional.
    """

    def filter_queryset(self, request, queryset, view):
        user = request.user

        # 1. Asegurar autenticación básica
        if not user.is_authenticated:
            return queryset.none()

        # 2. Bypass total para Superusuarios y Administradores del sistema
        if user.is_superuser or user.user_category == "ADMIN":
            return queryset

        model = queryset.model

        # 3. Lista blanca de Catálogos Públicos y Estructuras Curriculares Básicas (Lectura permitida)
        if model in PUBLIC_CATALOGS:
            return queryset

        # 4. Despacho dinámico basado en la categoría del usuario (Patrón Handler)
        user_type_code = user.user_category
        handler_class = ROLE_HANDLERS.get(user_type_code)
        if handler_class:
            return handler_class(user).filter(queryset)

        # Fallback de Seguridad Absoluta para cualquier otro tipo de usuario / modelo privado no explícito
        return queryset.none()
