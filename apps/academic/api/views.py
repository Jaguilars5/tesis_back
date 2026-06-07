from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.api.permissions import HasPermission
from apps.core.constants.permissions import academic
from ..repositories import (
    SubjectRepository,
    AcademicPeriodRepository,
    TeacherSubjectSectionRepository,
    SubjectAcademicConfigRepository,
    SubjectOfferingRepository,
    InterdisciplinaryProjectRepository,
    SubjectProjectRepository,
)
from .serializers import (
    SubjectSerializer,
    Academic_PeriodSerializer,
    Teacher_Subject_SectionSerializer,
    SubjectAcademicConfigSerializer,
    SubjectOfferingSerializer,
    InterdisciplinaryProjectSerializer,
    SubjectProjectSerializer,
)


@extend_schema_view(
    list=extend_schema(summary="Listar registros", tags=["academic"]),
    retrieve=extend_schema(summary="Obtener registro", tags=["academic"]),
    create=extend_schema(summary="Crear registro", tags=["academic"]),
    update=extend_schema(summary="Actualizar registro", tags=["academic"]),
    partial_update=extend_schema(summary="Actualizar parcialmente", tags=["academic"]),
    destroy=extend_schema(summary="Eliminar registro", tags=["academic"]),
    soft_delete=extend_schema(summary="Desactivar registro", tags=["academic"]),
)
class BaseAcademicViewSet(viewsets.ModelViewSet):
    """ViewSet base para modelos académicos con soporte de StandardResponse"""

    permission_classes = [IsAuthenticated, HasPermission]

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


class SubjectViewSet(BaseAcademicViewSet):
    serializer_class = SubjectSerializer
    action_permissions = {
        "list": academic.VIEW_SUBJECT,
        "retrieve": academic.VIEW_SUBJECT,
        "create": academic.CREATE_SUBJECT,
        "update": academic.UPDATE_SUBJECT,
        "partial_update": academic.UPDATE_SUBJECT,
        "destroy": academic.DELETE_SUBJECT,
        "soft_delete": academic.DELETE_SUBJECT,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = SubjectRepository()

    def get_queryset(self):
        return self.repository.get_all()


class AcademicPeriodViewSet(BaseAcademicViewSet):
    serializer_class = Academic_PeriodSerializer
    action_permissions = {
        "list": academic.VIEW_PERIOD,
        "retrieve": academic.VIEW_PERIOD,
        "create": academic.CREATE_PERIOD,
        "update": academic.UPDATE_PERIOD,
        "partial_update": academic.UPDATE_PERIOD,
        "destroy": academic.DELETE_PERIOD,
        "soft_delete": academic.DELETE_PERIOD,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = AcademicPeriodRepository()

    def get_queryset(self):
        return self.repository.get_all()


class TeacherSubjectSectionViewSet(BaseAcademicViewSet):
    serializer_class = Teacher_Subject_SectionSerializer
    action_permissions = {
        "list": academic.VIEW_TEACHER_SUBJECT,
        "retrieve": academic.VIEW_TEACHER_SUBJECT,
        "create": academic.CREATE_TEACHER_SUBJECT,
        "update": academic.UPDATE_TEACHER_SUBJECT,
        "partial_update": academic.UPDATE_TEACHER_SUBJECT,
        "destroy": academic.DELETE_TEACHER_SUBJECT,
        "soft_delete": academic.DELETE_TEACHER_SUBJECT,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = TeacherSubjectSectionRepository()

    def get_queryset(self):
        return self.repository.get_all()


class SubjectAcademicConfigViewSet(BaseAcademicViewSet):
    serializer_class = SubjectAcademicConfigSerializer
    action_permissions = {
        "list": academic.VIEW_SUBJECT,
        "retrieve": academic.VIEW_SUBJECT,
        "create": academic.CREATE_SUBJECT,
        "update": academic.UPDATE_SUBJECT,
        "partial_update": academic.UPDATE_SUBJECT,
        "destroy": academic.DELETE_SUBJECT,
        "soft_delete": academic.DELETE_SUBJECT,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = SubjectAcademicConfigRepository()

    def get_queryset(self):
        return self.repository.get_all()


class SubjectOfferingViewSet(BaseAcademicViewSet):
    serializer_class = SubjectOfferingSerializer
    action_permissions = {
        "list": academic.VIEW_SUBJECT,
        "retrieve": academic.VIEW_SUBJECT,
        "create": academic.CREATE_SUBJECT,
        "update": academic.UPDATE_SUBJECT,
        "partial_update": academic.UPDATE_SUBJECT,
        "destroy": academic.DELETE_SUBJECT,
        "soft_delete": academic.DELETE_SUBJECT,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = SubjectOfferingRepository()

    def get_queryset(self):
        return self.repository.get_all()


class InterdisciplinaryProjectViewSet(BaseAcademicViewSet):
    serializer_class = InterdisciplinaryProjectSerializer
    action_permissions = {
        "list": academic.VIEW_CONFIG,
        "retrieve": academic.VIEW_CONFIG,
        "create": academic.CREATE_CONFIG,
        "update": academic.UPDATE_CONFIG,
        "partial_update": academic.UPDATE_CONFIG,
        "destroy": academic.DELETE_CONFIG,
        "soft_delete": academic.DELETE_CONFIG,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = InterdisciplinaryProjectRepository()

    def get_queryset(self):
        return self.repository.get_all()


class SubjectProjectViewSet(BaseAcademicViewSet):
    serializer_class = SubjectProjectSerializer
    action_permissions = {
        "list": academic.VIEW_CONFIG,
        "retrieve": academic.VIEW_CONFIG,
        "create": academic.CREATE_CONFIG,
        "update": academic.UPDATE_CONFIG,
        "partial_update": academic.UPDATE_CONFIG,
        "destroy": academic.DELETE_CONFIG,
        "soft_delete": academic.DELETE_CONFIG,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = SubjectProjectRepository()

    def get_queryset(self):
        return self.repository.get_all()
