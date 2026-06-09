from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ...repositories import SyncOperationRepository, SyncStatusRepository
from ..serializers import SyncOperationSerializer, SyncStatusSerializer
from apps.core.api.permissions import HasPermission
from apps.core.api.pagination import StandardResultsSetPagination
from apps.core.constants.permissions import integration as perm


@extend_schema_view(
    list=extend_schema(summary="Listar operaciones de sincronización", tags=["integration"]),
    retrieve=extend_schema(summary="Obtener operación de sincronización", tags=["integration"]),
    create=extend_schema(summary="Crear operación de sincronización", tags=["integration"]),
    update=extend_schema(summary="Actualizar operación de sincronización", tags=["integration"]),
    partial_update=extend_schema(summary="Actualizar operación de sincronización parcialmente", tags=["integration"]),
    destroy=extend_schema(summary="Eliminar operación de sincronización", tags=["integration"]),
)
class SyncOperationViewSet(viewsets.ModelViewSet):
    serializer_class = SyncOperationSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": perm.VIEW_SYNC_OPERATION,
        "retrieve": perm.VIEW_SYNC_OPERATION,
        "create": perm.CREATE_SYNC_OPERATION,
        "update": perm.UPDATE_SYNC_OPERATION,
        "partial_update": perm.UPDATE_SYNC_OPERATION,
        "destroy": perm.DELETE_SYNC_OPERATION,
    }

    def get_queryset(self):
        return SyncOperationRepository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar estados de sincronización", tags=["integration"]),
    retrieve=extend_schema(summary="Obtener estado de sincronización", tags=["integration"]),
    create=extend_schema(summary="Crear estado de sincronización", tags=["integration"]),
    update=extend_schema(summary="Actualizar estado de sincronización", tags=["integration"]),
    partial_update=extend_schema(summary="Actualizar estado de sincronización parcialmente", tags=["integration"]),
    destroy=extend_schema(summary="Eliminar estado de sincronización", tags=["integration"]),
)
class SyncStatusViewSet(viewsets.ModelViewSet):
    serializer_class = SyncStatusSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": perm.VIEW_SYNC_STATUS,
        "retrieve": perm.VIEW_SYNC_STATUS,
        "create": perm.CREATE_SYNC_STATUS,
        "update": perm.UPDATE_SYNC_STATUS,
        "partial_update": perm.UPDATE_SYNC_STATUS,
        "destroy": perm.DELETE_SYNC_STATUS,
    }

    def get_queryset(self):
        return SyncStatusRepository.get_all()
