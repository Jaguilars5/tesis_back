from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.filters import OrderingFilter

from apps.institutions.api.base import BaseInstitutionsViewSet

from ..application.serializers import SchoolYearSerializer
from ..domain.services import SchoolYearService
from ..infrastructure.repositories import SchoolYearRepository
from ..permissions import ACTION_PERMISSIONS


@extend_schema_view(
    list=extend_schema(summary="Listar a\u00f1os escolares", tags=["institutions"]),
    get=extend_schema(summary="Obtener a\u00f1o escolar", tags=["institutions"]),
    create=extend_schema(summary="Crear a\u00f1o escolar", tags=["institutions"]),
    update=extend_schema(summary="Actualizar a\u00f1o escolar", tags=["institutions"]),
    partial_update=extend_schema(summary="Actualizar a\u00f1o escolar parcialmente", tags=["institutions"]),
    destroy=extend_schema(summary="Eliminar a\u00f1o escolar", tags=["institutions"]),
)
class SchoolYearViewSet(BaseInstitutionsViewSet):
    serializer_class = SchoolYearSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [OrderingFilter]
    ordering_fields = ["start_date", "end_date"]
    ordering = ["-start_date"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = SchoolYearRepository()

    def get_queryset(self):
        search = self.request.query_params.get("search")
        return self.repository.get_all(search=search)

    def perform_create(self, serializer):
        data = serializer.validated_data
        obj = SchoolYearService.create_school_year(
            start_date=data["start_date"],
            end_date=data["end_date"],
        )
        serializer.instance = obj

    def perform_update(self, serializer):
        data = dict(serializer.validated_data)
        obj = SchoolYearService.update_school_year(serializer.instance.id, **data)
        serializer.instance = obj

    def perform_destroy(self, instance):
        SchoolYearService.deactivate_school_year(instance.id)
