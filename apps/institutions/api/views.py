from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.api.permissions import HasPermission
from apps.core.constants.permissions import institutions

from ..services.institution_service import InstitutionService
from ..models import AcademicGrade, AcademicLevel, DocumentType, School_Year, Section
from ..repositories.section_repository import SectionRepository
from .serializers import (
    AcademicGradeSerializer,
    AcademicLevelSerializer,
    DocumentTypeSerializer,
    School_YearSerializer,
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
)
class BaseInstitutionsViewSet(viewsets.ModelViewSet):
    """ViewSet base para modelos de instituciones con soporte de StandardResponse"""

    permission_classes = [permissions.IsAuthenticated, HasPermission]

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
        if hasattr(instance, "active"):
            instance.active = False
            instance.save()
            return Response({"id": instance.id, "active": False})
        return Response("Este modelo no soporta borrado lógico", status=400)


class SchoolYearViewSet(BaseInstitutionsViewSet):
    serializer_class = School_YearSerializer
    action_permissions = {
        "list": institutions.VIEW_SCHOOL_YEAR,
        "retrieve": institutions.VIEW_SCHOOL_YEAR,
        "create": institutions.CREATE_SCHOOL_YEAR,
        "update": institutions.UPDATE_SCHOOL_YEAR,
        "partial_update": institutions.UPDATE_SCHOOL_YEAR,
        "destroy": institutions.DELETE_SCHOOL_YEAR,
        "list_by_institution": institutions.VIEW_SCHOOL_YEAR,
        "get_by_id": institutions.VIEW_SCHOOL_YEAR,
        "add_school_year": institutions.CREATE_SCHOOL_YEAR,
        "update_school_year": institutions.UPDATE_SCHOOL_YEAR,
        "soft_delete_school_year": institutions.DELETE_SCHOOL_YEAR,
    }

    def get_queryset(self):
        return School_Year.objects.filter(active=True).order_by("-start_date")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            school_year = InstitutionService.create_school_year(
                name=serializer.validated_data["name"],
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
    list=extend_schema(summary="Listar tipos de documento", tags=["institutions"]),
    retrieve=extend_schema(summary="Obtener tipo de documento", tags=["institutions"]),
)
class DocumentTypeViewSet(BaseInstitutionsViewSet):
    serializer_class = DocumentTypeSerializer
    action_permissions = {
        "list": institutions.VIEW_DOCUMENT_TYPE,
        "retrieve": institutions.VIEW_DOCUMENT_TYPE,
    }

    def get_queryset(self):
        return DocumentType.objects.all().order_by("name")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return Response(str(e), status=400)


@extend_schema_view(
    list=extend_schema(summary="Listar niveles académicos", tags=["institutions"]),
    retrieve=extend_schema(summary="Obtener nivel académico", tags=["institutions"]),
    create=extend_schema(summary="Crear nivel académico", tags=["institutions"]),
    update=extend_schema(summary="Actualizar nivel académico", tags=["institutions"]),
    partial_update=extend_schema(
        summary="Actualizar nivel parcialmente", tags=["institutions"]
    ),
    destroy=extend_schema(summary="Eliminar nivel académico", tags=["institutions"]),
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
    }

    def get_queryset(self):
        return AcademicLevel.objects.all().order_by("name")


@extend_schema_view(
    list=extend_schema(summary="Listar grados académicos", tags=["institutions"]),
    retrieve=extend_schema(summary="Obtener grado académico", tags=["institutions"]),
    create=extend_schema(summary="Crear grado académico", tags=["institutions"]),
    update=extend_schema(summary="Actualizar grado académico", tags=["institutions"]),
    partial_update=extend_schema(
        summary="Actualizar grado parcialmente", tags=["institutions"]
    ),
    destroy=extend_schema(summary="Eliminar grado académico", tags=["institutions"]),
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
    }

    def get_queryset(self):
        return AcademicGrade.objects.all().order_by("sequence_order")


@extend_schema_view(
    list=extend_schema(summary="Listar secciones", tags=["institutions"]),
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = SectionRepository()

    def get_queryset(self):
        return self.repository.get_all()
