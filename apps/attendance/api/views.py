from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    AbsenceTypeSerializer,
    AttendanceSerializer,
    AttendanceStatusSerializer,
)
from ..repositories import (
    AbsenceTypeRepository,
    AttendanceRepository,
    AttendanceStatusRepository,
)
from apps.core.api.permissions import HasPermission
from apps.core.api.pagination import StandardResultsSetPagination
from apps.core.constants.permissions import attendance as perm


@extend_schema_view(
    list=extend_schema(summary="Listar asistencias", tags=["attendance"]),
    retrieve=extend_schema(summary="Obtener asistencia", tags=["attendance"]),
    create=extend_schema(summary="Registrar asistencia", tags=["attendance"]),
    update=extend_schema(summary="Actualizar asistencia", tags=["attendance"]),
    partial_update=extend_schema(summary="Actualizar asistencia parcialmente", tags=["attendance"]),
    destroy=extend_schema(summary="Eliminar asistencia", tags=["attendance"]),
)
class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": perm.VIEW_ATTENDANCE,
        "retrieve": perm.VIEW_ATTENDANCE,
        "create": perm.CREATE_ATTENDANCE,
        "update": perm.UPDATE_ATTENDANCE,
        "partial_update": perm.UPDATE_ATTENDANCE,
        "destroy": perm.DELETE_ATTENDANCE,
    }

    def get_queryset(self):
        return AttendanceRepository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar estados de asistencia", tags=["attendance"]),
    retrieve=extend_schema(summary="Obtener estado de asistencia", tags=["attendance"]),
    create=extend_schema(summary="Crear estado de asistencia", tags=["attendance"]),
    update=extend_schema(summary="Actualizar estado de asistencia", tags=["attendance"]),
    partial_update=extend_schema(summary="Actualizar estado parcialmente", tags=["attendance"]),
    destroy=extend_schema(summary="Eliminar estado de asistencia", tags=["attendance"]),
)
class AttendanceStatusViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceStatusSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": perm.VIEW_ATTENDANCE_STATUS,
        "retrieve": perm.VIEW_ATTENDANCE_STATUS,
        "create": perm.CREATE_ATTENDANCE_STATUS,
        "update": perm.UPDATE_ATTENDANCE_STATUS,
        "partial_update": perm.UPDATE_ATTENDANCE_STATUS,
        "destroy": perm.DELETE_ATTENDANCE_STATUS,
    }

    def get_queryset(self):
        return AttendanceStatusRepository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar tipos de ausencia", tags=["attendance"]),
    retrieve=extend_schema(summary="Obtener tipo de ausencia", tags=["attendance"]),
    create=extend_schema(summary="Crear tipo de ausencia", tags=["attendance"]),
    update=extend_schema(summary="Actualizar tipo de ausencia", tags=["attendance"]),
    partial_update=extend_schema(summary="Actualizar tipo de ausencia parcialmente", tags=["attendance"]),
    destroy=extend_schema(summary="Eliminar tipo de ausencia", tags=["attendance"]),
)
class AbsenceTypeViewSet(viewsets.ModelViewSet):
    serializer_class = AbsenceTypeSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": perm.VIEW_ABSENCE_TYPE,
        "retrieve": perm.VIEW_ABSENCE_TYPE,
        "create": perm.CREATE_ABSENCE_TYPE,
        "update": perm.UPDATE_ABSENCE_TYPE,
        "partial_update": perm.UPDATE_ABSENCE_TYPE,
        "destroy": perm.DELETE_ABSENCE_TYPE,
    }

    def get_queryset(self):
        return AbsenceTypeRepository.get_all()
