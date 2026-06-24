from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.filters import OrderingFilter

from apps.institutions.api.base import BaseInstitutionsViewSet

from ..application.serializers import AcademicSublevelSerializer
from ..domain.services import AcademicSublevelService
from ..infrastructure.repositories import AcademicSublevelRepository
from ..permissions import ACTION_PERMISSIONS


@extend_schema_view(
    list=extend_schema(summary="Listar subniveles acad\u00e9micos", tags=["institutions"]),
    get=extend_schema(summary="Obtener subnivel acad\u00e9mico", tags=["institutions"]),
    create=extend_schema(summary="Crear subnivel acad\u00e9mico", tags=["institutions"]),
    update=extend_schema(summary="Actualizar subnivel acad\u00e9mico", tags=["institutions"]),
    partial_update=extend_schema(summary="Actualizar subnivel parcialmente", tags=["institutions"]),
    destroy=extend_schema(summary="Eliminar subnivel acad\u00e9mico", tags=["institutions"]),
)
class AcademicSublevelViewSet(BaseInstitutionsViewSet):
    serializer_class = AcademicSublevelSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [OrderingFilter]
    ordering_fields = ["name", "code"]
    ordering = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = AcademicSublevelRepository()

    def get_queryset(self):
        search = self.request.query_params.get("search")
        return self.repository.get_all(search=search)

    def perform_create(self, serializer):
        data = serializer.validated_data
        obj = AcademicSublevelService.create_academic_sublevel(
            academic_level_id=data["academic_level"].id,
            code=data["code"],
            name=data["name"],
            description=data.get("description", ""),
        )
        serializer.instance = obj

    def perform_update(self, serializer):
        data = dict(serializer.validated_data)
        obj = AcademicSublevelService.update_academic_sublevel(
            serializer.instance.id, **data
        )
        serializer.instance = obj
