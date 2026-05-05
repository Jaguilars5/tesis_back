"""
Vistas de API para el módulo Grading.

Utiliza ViewSets de DRF para operaciones CRUD RESTful sobre calificaciones,
asistencia e incidentes de conducta.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.core.pagination import StandardResultsSetPagination
from apps.core.permissions import HasPermission
from apps.core.constants.permissions import grading
from apps.core.utils import ok_response, error_response

from ..repositories import (
    AttendanceRepository,
    ConductIncidentRepository,
    StudentNoteRepository,
)
from .serializers import (
    AttendanceSerializer,
    ConductIncidentSerializer,
    StudentNoteSerializer,
)


@extend_schema_view(
    list=extend_schema(summary="Listar registros", tags=["grading"]),
    retrieve=extend_schema(summary="Obtener registro", tags=["grading"]),
    create=extend_schema(summary="Crear registro", tags=["grading"]),
    update=extend_schema(summary="Actualizar registro", tags=["grading"]),
    partial_update=extend_schema(summary="Actualizar parcialmente", tags=["grading"]),
    destroy=extend_schema(summary="Eliminar registro", tags=["grading"]),
)
class BaseGradingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasPermission]
    pagination_class = StandardResultsSetPagination

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.repository.get_by_id(kwargs.get("pk"))
            if not instance:
                return error_response(
                    f"{self.serializer_class.Meta.model.__name__} not found",
                    404,
                )
            serializer = self.get_serializer(instance)
            return ok_response(serializer.data)
        except Exception as e:
            return error_response(e)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return ok_response(serializer.data, status=201)
            return error_response(serializer.errors)
        except Exception as e:
            return error_response(e)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.repository.get_by_id(kwargs.get("pk"))
            if not instance:
                return error_response(
                    f"{self.serializer_class.Meta.model.__name__} not found",
                    404,
                )
            partial = kwargs.pop("partial", False)
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            if serializer.is_valid():
                serializer.save()
                return ok_response(serializer.data)
            return error_response(serializer.errors)
        except Exception as e:
            return error_response(e)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.repository.get_by_id(kwargs.get("pk"))
            if not instance:
                return error_response(
                    f"{self.serializer_class.Meta.model.__name__} not found",
                    404,
                )
            if hasattr(instance, "active"):
                instance.active = False
                instance.save()
                return ok_response({"id": kwargs.get("pk"), "active": False})
            return error_response(
                f"{self.serializer_class.Meta.model.__name__} does not support soft delete."
            )
        except Exception as e:
            return error_response(e)


class StudentNoteViewSet(BaseGradingViewSet):
    serializer_class = StudentNoteSerializer
    action_permissions = {
        "list": grading.VIEW_NOTE,
        "retrieve": grading.VIEW_NOTE,
        "create": grading.CREATE_NOTE,
        "update": grading.UPDATE_NOTE,
        "partial_update": grading.UPDATE_NOTE,
        "destroy": grading.DELETE_NOTE,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = StudentNoteRepository()

    def get_queryset(self):
        return self.repository.get_all()


class AttendanceViewSet(BaseGradingViewSet):
    serializer_class = AttendanceSerializer
    action_permissions = {
        "list": grading.VIEW_ATTENDANCE,
        "retrieve": grading.VIEW_ATTENDANCE,
        "create": grading.CREATE_ATTENDANCE,
        "update": grading.UPDATE_ATTENDANCE,
        "partial_update": grading.UPDATE_ATTENDANCE,
        "destroy": grading.DELETE_ATTENDANCE,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = AttendanceRepository()

    def get_queryset(self):
        return self.repository.get_all()


class ConductIncidentViewSet(BaseGradingViewSet):
    serializer_class = ConductIncidentSerializer
    action_permissions = {
        "list": grading.VIEW_INCIDENT,
        "retrieve": grading.VIEW_INCIDENT,
        "create": grading.CREATE_INCIDENT,
        "update": grading.UPDATE_INCIDENT,
        "partial_update": grading.UPDATE_INCIDENT,
        "destroy": grading.DELETE_INCIDENT,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = ConductIncidentRepository()

    def get_queryset(self):
        return self.repository.get_all()
