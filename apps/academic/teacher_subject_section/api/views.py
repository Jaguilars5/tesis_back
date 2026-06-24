from drf_spectacular.utils import extend_schema, extend_schema_view

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter

from apps.academic.api.base import BaseAcademicViewSet
from apps.core.utils import ok_response, error_response

from ..application.serializers import TeacherSubjectSectionSerializer
from ..domain.services import TeacherSubjectSectionService
from ..infrastructure.repositories import TeacherSubjectSectionRepository
from ..permissions import ACTION_PERMISSIONS
from .filters import TeacherSubjectSectionFilter


@extend_schema_view(
    list=extend_schema(summary="Listar asignaciones docente-materia", tags=["academic"]),
    get=extend_schema(summary="Obtener asignación docente-materia", tags=["academic"]),
    create=extend_schema(summary="Asignar docente a materia", tags=["academic"]),
    update=extend_schema(summary="Actualizar asignación docente-materia", tags=["academic"]),
    partial_update=extend_schema(summary="Actualizar parcialmente asignación docente-materia", tags=["academic"]),
    destroy=extend_schema(summary="Eliminar asignación docente-materia", tags=["academic"]),
    soft_delete=extend_schema(summary="Desactivar asignación docente-materia", tags=["academic"]),
)
class TeacherSubjectSectionViewSet(BaseAcademicViewSet):
    serializer_class = TeacherSubjectSectionSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_class = TeacherSubjectSectionFilter
    search_fields = [
        "user__person__names",
        "user__person__last_names",
        "user__username",
        "user__email",
        "subject_offering__section__school_year__name",
        "subject_offering__section__academic_grade__name",
        "subject_offering__section__parallel",
        "subject_offering__subject_academic_config__subject__name",
    ]
    ordering_fields = ["id", "created_at", "is_active"]
    ordering = ["-id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = TeacherSubjectSectionRepository()

    def get_queryset(self):
        return self.repository.get_all().select_related(
            "user__person",
            "subject_offering__section__school_year",
            "subject_offering__section__academic_grade",
            "subject_offering__subject_academic_config__subject",
            "subject_offering__subject_academic_config__academic_grade",
        )

    def perform_create(self, serializer):
        data = serializer.validated_data
        instance = TeacherSubjectSectionService.assign_teacher(
            user_id=data["user"].id,
            subject_offering_id=data["subject_offering"].id,
        )
        serializer.instance = instance
