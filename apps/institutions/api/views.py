from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.api.permissions import HasPermission
from apps.core.constants.permissions import institutions

from ..services.institution_service import InstitutionService
from ..repositories import (
    AcademicGradeRepository,
    AcademicLevelRepository,
    AcademicSublevelRepository,
    SchoolYearRepository,
    SectionRepository,
)
from .serializers import (
    AcademicGradeSerializer,
    AcademicLevelSerializer,
    AcademicSublevelSerializer,
    SchoolYearSerializer,
    SectionSerializer,
)


@extend_schema_view(
    list=extend_schema(summary="Listar años escolares", tags=["institutions"]),
    retrieve=extend_schema(summary="Obtener año escolar", tags=["institutions"]),
    create=extend_schema(summary="Crear año escolar", tags=["institutions"]),
    update=extend_schema(summary="Actualizar año escolar", tags=["institutions"]),
    partial_update=extend_schema(
        summary="Actualizar año escolar parcialmente", tags=["institutions"]
    ),
    destroy=extend_schema(summary="Eliminar año escolar", tags=["institutions"]),
    soft_delete=extend_schema(
        summary="Desactivar año escolar (borrado lógico)", tags=["institutions"]
    ),
)
class BaseInstitutionsViewSet(viewsets.ModelViewSet):
    """ViewSet base para modelos de instituciones con soporte de StandardResponse"""

    permission_classes = [permissions.IsAuthenticated, HasPermission]
    repository = None

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=["post"], url_path="soft-delete")
    def soft_delete(self, request, pk=None):
        instance = self.get_object()
        if hasattr(instance, "is_active"):
            instance.is_active = False
            instance.save()
            return Response({"id": instance.id, "is_active": False})
        return Response("Este modelo no soporta borrado lógico", status=400)


@extend_schema_view(
    list=extend_schema(
        summary="Listar años escolares",
        tags=["institutions"],
        parameters=[
            OpenApiParameter(name="search", description="Filtrar por nombre del año escolar (ej: ?search=2024)", required=False, type=str),
        ],
    ),
)
class SchoolYearViewSet(BaseInstitutionsViewSet):
    serializer_class = SchoolYearSerializer
    action_permissions = {
        "list": institutions.VIEW_SCHOOL_YEAR,
        "retrieve": institutions.VIEW_SCHOOL_YEAR,
        "create": institutions.CREATE_SCHOOL_YEAR,
        "update": institutions.UPDATE_SCHOOL_YEAR,
        "partial_update": institutions.UPDATE_SCHOOL_YEAR,
        "destroy": institutions.DELETE_SCHOOL_YEAR,
        "soft_delete": institutions.DELETE_SCHOOL_YEAR,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = SchoolYearRepository()

    ordering_fields = ["start_date", "end_date"]
    ordering = ["-start_date"]
    _ORDERING_ALIASES = {
        "name": "start_date",
        "-name": "-start_date",
    }

    def get_queryset(self):
        search = self.request.query_params.get("search")
        return self.repository.get_all(search=search)

    def get_ordering(self):
        ordering = self.request.query_params.get(self.ordering_param)
        if ordering in self._ORDERING_ALIASES:
            return [self._ORDERING_ALIASES[ordering]]
        return super().get_ordering()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            school_year = InstitutionService.create_school_year(
                start_date=serializer.validated_data["start_date"],
                end_date=serializer.validated_data["end_date"],
            )
            return Response(self.get_serializer(school_year).data, status=201)
        except ValueError as e:
            return Response(str(e), status=400)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(
            self.get_object(), data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        try:
            school_year = InstitutionService.update_school_year(
                kwargs["pk"], **serializer.validated_data
            )
            return Response(self.get_serializer(school_year).data)
        except ValueError as e:
            return Response(str(e), status=400)

    def destroy(self, request, *args, **kwargs):
        try:
            InstitutionService.deactivate_school_year(kwargs["pk"])
            return Response({"id": kwargs["pk"], "active": False})
        except ValueError as e:
            return Response(str(e), status=400)


@extend_schema_view(
    list=extend_schema(
        summary="Listar niveles académicos",
        tags=["institutions"],
        parameters=[
            OpenApiParameter(name="search", description="Filtrar por nombre del nivel (ej: ?search=basica)", required=False, type=str),
        ],
    ),
    retrieve=extend_schema(summary="Obtener nivel académico", tags=["institutions"]),
    create=extend_schema(summary="Crear nivel académico", tags=["institutions"]),
    update=extend_schema(summary="Actualizar nivel académico", tags=["institutions"]),
    partial_update=extend_schema(
        summary="Actualizar nivel parcialmente", tags=["institutions"]
    ),
    destroy=extend_schema(summary="Eliminar nivel académico", tags=["institutions"]),
    soft_delete=extend_schema(
        summary="Desactivar nivel académico (borrado lógico)", tags=["institutions"]
    ),
)
class AcademicLevelViewSet(BaseInstitutionsViewSet):
    serializer_class = AcademicLevelSerializer
    action_permissions = {
        "list": institutions.VIEW_ACADEMIC_LEVEL,
        "retrieve": institutions.VIEW_ACADEMIC_LEVEL,
        "create": institutions.CREATE_ACADEMIC_LEVEL,
        "update": institutions.UPDATE_ACADEMIC_LEVEL,
        "partial_update": institutions.UPDATE_ACADEMIC_LEVEL,
        "destroy": institutions.DELETE_ACADEMIC_LEVEL,
        "soft_delete": institutions.DELETE_ACADEMIC_LEVEL,
    }

    ordering_fields = ["name"]
    ordering = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = AcademicLevelRepository()

    def get_queryset(self):
        search = self.request.query_params.get("search")
        return self.repository.get_all(search=search)


@extend_schema_view(
    list=extend_schema(
        summary="Listar subleveles académicos",
        tags=["institutions"],
        parameters=[
            OpenApiParameter(name="search", description="Filtrar por nombre del sublevel (ej: ?search=basica)", required=False, type=str),
        ],
    ),
    retrieve=extend_schema(summary="Obtener sublevel académico", tags=["institutions"]),
    create=extend_schema(summary="Crear sublevel académico", tags=["institutions"]),
    update=extend_schema(summary="Actualizar sublevel académico", tags=["institutions"]),
    partial_update=extend_schema(
        summary="Actualizar sublevel parcialmente", tags=["institutions"]
    ),
    destroy=extend_schema(summary="Eliminar sublevel académico", tags=["institutions"]),
    soft_delete=extend_schema(
        summary="Desactivar sublevel académico (borrado lógico)", tags=["institutions"]
    ),
)
class AcademicSublevelViewSet(BaseInstitutionsViewSet):
    serializer_class = AcademicSublevelSerializer
    action_permissions = {
        "list": institutions.VIEW_ACADEMIC_SUBLEVEL,
        "retrieve": institutions.VIEW_ACADEMIC_SUBLEVEL,
        "create": institutions.CREATE_ACADEMIC_SUBLEVEL,
        "update": institutions.UPDATE_ACADEMIC_SUBLEVEL,
        "partial_update": institutions.UPDATE_ACADEMIC_SUBLEVEL,
        "destroy": institutions.DELETE_ACADEMIC_SUBLEVEL,
        "soft_delete": institutions.DELETE_ACADEMIC_SUBLEVEL,
    }

    ordering_fields = ["name", "code"]
    ordering = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = AcademicSublevelRepository()

    def get_queryset(self):
        search = self.request.query_params.get("search")
        return self.repository.get_all(search=search)


@extend_schema_view(
    list=extend_schema(
        summary="Listar grados académicos",
        tags=["institutions"],
        parameters=[
            OpenApiParameter(name="search", description="Filtrar por nombre del grado (ej: ?search=segundo)", required=False, type=str),
        ],
    ),
    retrieve=extend_schema(summary="Obtener grado académico", tags=["institutions"]),
    create=extend_schema(summary="Crear grado académico", tags=["institutions"]),
    update=extend_schema(summary="Actualizar grado académico", tags=["institutions"]),
    partial_update=extend_schema(
        summary="Actualizar grado parcialmente", tags=["institutions"]
    ),
    destroy=extend_schema(summary="Eliminar grado académico", tags=["institutions"]),
    soft_delete=extend_schema(
        summary="Desactivar grado académico (borrado lógico)", tags=["institutions"]
    ),
)
class AcademicGradeViewSet(BaseInstitutionsViewSet):
    serializer_class = AcademicGradeSerializer
    action_permissions = {
        "list": institutions.VIEW_ACADEMIC_GRADE,
        "retrieve": institutions.VIEW_ACADEMIC_GRADE,
        "create": institutions.CREATE_ACADEMIC_GRADE,
        "update": institutions.UPDATE_ACADEMIC_GRADE,
        "partial_update": institutions.UPDATE_ACADEMIC_GRADE,
        "destroy": institutions.DELETE_ACADEMIC_GRADE,
        "soft_delete": institutions.DELETE_ACADEMIC_GRADE,
    }

    ordering_fields = ["name"]
    ordering = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = AcademicGradeRepository()

    def get_queryset(self):
        search = self.request.query_params.get("search")
        return self.repository.get_all(search=search)


@extend_schema_view(
    list=extend_schema(
        summary="Listar secciones",
        tags=["institutions"],
        parameters=[
            OpenApiParameter(name="search", description="Filtrar por paralelo de la sección (ej: ?search=A)", required=False, type=str),
        ],
    ),
    retrieve=extend_schema(summary="Obtener sección", tags=["institutions"]),
    create=extend_schema(summary="Crear sección", tags=["institutions"]),
    update=extend_schema(summary="Actualizar sección", tags=["institutions"]),
    partial_update=extend_schema(
        summary="Actualizar sección parcialmente", tags=["institutions"]
    ),
    destroy=extend_schema(summary="Eliminar sección", tags=["institutions"]),
    soft_delete=extend_schema(
        summary="Desactivar sección (borrado lógico)", tags=["institutions"]
    ),
)
class SectionViewSet(BaseInstitutionsViewSet):
    """ViewSet para el modelo Section (ubicado en institutions)"""

    serializer_class = SectionSerializer
    action_permissions = {
        "list": institutions.VIEW_SECTION,
        "retrieve": institutions.VIEW_SECTION,
        "create": institutions.CREATE_SECTION,
        "update": institutions.UPDATE_SECTION,
        "partial_update": institutions.UPDATE_SECTION,
        "destroy": institutions.DELETE_SECTION,
        "soft_delete": institutions.DELETE_SECTION,
    }

    ordering_fields = ["parallel", "capacity"]
    ordering = ["academic_grade__name", "parallel"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = SectionRepository()

    def get_queryset(self):
        search = self.request.query_params.get("search")
        return self.repository.get_all(search=search)
