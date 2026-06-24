"""
Vista base para todos los ViewSets del módulo Analytics.

Siguiendo el patrón de apps/academic/api/base.py, proporciona:
- Respuestas estandarizadas con ok_response()
- Paginación estándar
- Permisos HasPermission + IsAuthenticated
- Mapeo de 'retrieve' a 'get' para compatibilidad con AnalyticsRouter
"""

from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from apps.core.api.mixins import SoftDeleteModelMixin
from apps.core.api.pagination import StandardResultsSetPagination
from apps.core.api.permissions import HasPermission
from apps.core.utils import ok_response


class BaseAnalyticsViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    SoftDeleteModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet base para módulos de Analytics.

    Todas las respuestas usan el formato estándar {"ok", "data", "msg"}.
    Las operaciones de lectura usan el repositorio inyectado en get_queryset().
    Las operaciones de escritura deben sobreescribir perform_create/update.
    """

    permission_classes = [IsAuthenticated, HasPermission]
    pagination_class = StandardResultsSetPagination

    def initial(self, request, *args, **kwargs):
        """Mapea la acción 'retrieve' a 'get' para usar AnalyticsRouter."""
        if self.action == "retrieve":
            self.action = "get"
        super().initial(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Obtener un registro por ID (reemplaza retrieve)."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ok_response(serializer.data)

    def list(self, request, *args, **kwargs):
        """Listar registros con paginación opcional."""
        queryset = self.filter_queryset(self.get_queryset())
        if self.paginator is not None:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return ok_response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Crear un nuevo registro."""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)
        self.perform_create(serializer)
        return ok_response(
            serializer.data,
            msg="Creado exitosamente",
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        """Actualizar un registro existente."""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)
        self.perform_update(serializer)
        return ok_response(serializer.data, msg="Actualizado exitosamente")

    def destroy(self, request, *args, **kwargs):
        """Eliminar un registro (soft delete si está habilitado)."""
        instance = self.get_object()
        self.perform_destroy(instance)
        return ok_response(msg="Eliminado exitosamente")
