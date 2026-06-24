from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.filters import OrderingFilter

from apps.institutions.api.base import BaseInstitutionsViewSet

from ..application.serializers import AcademicLevelSerializer
from ..domain.services import AcademicLevelService
from ..infrastructure.repositories import AcademicLevelRepository
from ..permissions import ACTION_PERMISSIONS


@extend_schema_view(
    list=extend_schema(summary="Listar niveles acad\u00e9micos", tags=["institutions"]),
    get=extend_schema(summary="Obtener nivel acad\u00e9mico", tags=["institutions"]),
    create=extend_schema(summary="Crear nivel acad\u00e9mico", tags=["institutions"]),
    update=extend_schema(summary="Actualizar nivel acad\u00e9mico", tags=["institutions"]),
    partial_update=extend_schema(summary="Actualizar nivel parcialmente", tags=["institutions"]),
    destroy=extend_schema(summary="Eliminar nivel acad\u00e9mico", tags=["institutions"]),
)
class AcademicLevelViewSet(BaseInstitutionsViewSet):
    serializer_class = AcademicLevelSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [OrderingFilter]
    ordering_fields = ["name"]
    ordering = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = AcademicLevelRepository()

    def get_queryset(self):
        search = self.request.query_params.get("search")
        return self.repository.get_all(search=search)

    def perform_create(self, serializer):
        data = serializer.validated_data
        obj = AcademicLevelService.create_academic_level(
            name=data["name"],
            code=data.get("code", ""),
        )
        serializer.instance = obj

    def perform_update(self, serializer):
        data = dict(serializer.validated_data)
        obj = AcademicLevelService.update_academic_level(serializer.instance.id, **data)
        serializer.instance = obj
