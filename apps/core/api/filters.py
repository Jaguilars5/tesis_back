from rest_framework.filters import BaseFilterBackend

# Importar los modelos necesarios para la validación tipada de catálogos públicos
from apps.institutions.models import DocumentType, School_Year, AcademicLevel, AcademicGrade, Section
from apps.academic.models import Academic_Period, Subject, SubjectAcademicConfig, SubjectOffering
from apps.students.models import EnrollmentStatus
from apps.grading.models import GradeType, QualitativeScale
from apps.attendance.models import AttendanceStatus, IncidentType, SocioemotionalSkill
from apps.analytics.models import RiskFactor

from .role_handlers import ROLE_HANDLERS

# Definir la lista blanca de catálogos públicos usando tipos reales (clases)
PUBLIC_CATALOGS = {
    DocumentType,
    School_Year,
    Academic_Period,
    AcademicLevel,
    AcademicGrade,
    Subject,
    SubjectAcademicConfig,
    SubjectOffering,
    Section,
    EnrollmentStatus,
    GradeType,
    QualitativeScale,
    AttendanceStatus,
    IncidentType,
    SocioemotionalSkill,
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
        if user.is_superuser or user.user_type == "ADMIN":
            return queryset

        model = queryset.model

        # 3. Lista blanca de Catálogos Públicos y Estructuras Curriculares Básicas (Lectura permitida)
        if model in PUBLIC_CATALOGS:
            return queryset

        # 4. Despacho dinámico basado en el tipo de rol del usuario (Patrón Handler)
        handler_class = ROLE_HANDLERS.get(user.user_type)
        if handler_class:
            return handler_class(user).filter(queryset)

        # Fallback de Seguridad Absoluta para cualquier otro tipo de usuario / modelo privado no explícito
        return queryset.none()
