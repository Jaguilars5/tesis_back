from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ...repositories import ConfigRepository
from ..serializers import SystemConfigSerializer
from apps.core.api.permissions import HasPermission
from apps.core.api.pagination import StandardResultsSetPagination


class SystemConfigViewSet(viewsets.ModelViewSet):
    serializer_class = SystemConfigSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    lookup_field = "key"
    action_permissions = {
        "list": "configuration.view_systemconfig",
        "retrieve": "configuration.view_systemconfig",
        "create": "configuration.create_systemconfig",
        "update": "configuration.update_systemconfig",
        "partial_update": "configuration.update_systemconfig",
        "destroy": "configuration.delete_systemconfig",
    }

    def get_queryset(self):
        return ConfigRepository.get_all()
