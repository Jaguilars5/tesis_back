from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError

from drf_spectacular.utils import extend_schema, extend_schema_view
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.analytics.api.base import BaseAnalyticsViewSet
from apps.core.utils import ok_response, error_response

from ..permissions import ACTION_PERMISSIONS
from ..application.serializers import EarlyAlertSerializer
from ..domain.services import EarlyAlertService
from .filters import EarlyAlertFilter


def _raise_validation_error(exc: ValueError) -> None:
    errors = (
        exc.args[0]
        if exc.args and isinstance(exc.args[0], dict)
        else {"non_field_errors": str(exc)}
    )
    raise DRFValidationError(errors) from exc


@extend_schema_view(
    list=extend_schema(summary="Listar alertas tempranas", tags=["analytics"]),
    get=extend_schema(summary="Obtener alerta temprana", tags=["analytics"]),
    mark_attended=extend_schema(
        summary="Marcar alerta como atendida", tags=["analytics"]
    ),
)
class EarlyAlertViewSet(BaseAnalyticsViewSet):
    serializer_class = EarlyAlertSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = EarlyAlertFilter
    search_fields = [
        "enrollment__student__person__names",
        "enrollment__student__person__last_names",
        "description",
    ]
    ordering_fields = ["detected_at", "urgency_level", "attended"]
    ordering = ["-detected_at"]

    def get_queryset(self):
        return EarlyAlertService.repository.get_all(active_only=False)

    def create(self, request, *args, **kwargs):
        return error_response(
            "Las alertas son generadas automaticamente por el sistema",
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def update(self, request, *args, **kwargs):
        return error_response(
            "Las alertas no pueden ser modificadas manualmente",
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def partial_update(self, request, *args, **kwargs):
        return error_response(
            "Las alertas no pueden ser modificadas manualmente",
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def destroy(self, request, *args, **kwargs):
        return error_response(
            "Las alertas no pueden ser eliminadas manualmente",
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(detail=True, methods=["post"])
    def mark_attended(self, request, pk=None):
        try:
            alert = self.get_object()
            actions = request.data.get("response_actions", "")
            alert = EarlyAlertService.mark_as_attended(
                alert.id, request.user.id, actions
            )
            return ok_response(
                EarlyAlertSerializer(alert).data,
                msg="Alerta marcada como atendida",
            )
        except ValueError as exc:
            _raise_validation_error(exc)
