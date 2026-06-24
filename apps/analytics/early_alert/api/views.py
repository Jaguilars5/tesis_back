"""
ViewSets de API para alertas tempranas.

Usa BaseAnalyticsViewSet para respuestas estandarizadas.
"""

from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.decorators import action

from apps.analytics.api.base import BaseAnalyticsViewSet
from apps.core.utils import ok_response, error_response
from drf_spectacular.utils import extend_schema, extend_schema_view

from ..permissions import ACTION_PERMISSIONS
from ..application.serializers import EarlyAlertSerializer
from ..infrastructure.repositories import EarlyAlertRepository
from ..domain.services import EarlyAlertService


def _raise_validation_error(exc: ValueError) -> None:
    """Convierte ValueError con dict de errores a DRF ValidationError."""
    errors = (
        exc.args[0]
        if exc.args and isinstance(exc.args[0], dict)
        else {"non_field_errors": str(exc)}
    )
    raise DRFValidationError(errors) from exc


@extend_schema_view(
    list=extend_schema(summary="Listar alertas tempranas", tags=["analytics"]),
    get=extend_schema(summary="Obtener alerta temprana", tags=["analytics"]),
    create=extend_schema(summary="Crear alerta temprana", tags=["analytics"]),
    update=extend_schema(summary="Actualizar alerta temprana", tags=["analytics"]),
    destroy=extend_schema(summary="Eliminar alerta temprana", tags=["analytics"]),
    mark_attended=extend_schema(
        summary="Marcar alerta como atendida", tags=["analytics"]
    ),
)
class EarlyAlertViewSet(BaseAnalyticsViewSet):
    """
    ViewSet para gestión de alertas tempranas.

    Proporciona operaciones CRUD + acción custom mark_attended.
    Todas las respuestas usan el formato estándar {"ok", "data", "msg"}.
    """

    serializer_class = EarlyAlertSerializer
    action_permissions = ACTION_PERMISSIONS
    filterset_class = None  # Se puede agregar EarlyAlertFilter si se necesita

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = EarlyAlertRepository()

    def get_queryset(self):
        """Obtiene el queryset desde el repositorio."""
        return self.repository.get_all()

    def perform_create(self, serializer):
        """Crea la alerta a través del repositorio."""
        data = serializer.validated_data
        try:
            from ..application import validators

            errors = validators.run_all_validators(
                enrollment_id=data["enrollment"].id
                if hasattr(data["enrollment"], "id")
                else data["enrollment"],
                academic_period_id=data["academic_period"].id
                if hasattr(data["academic_period"], "id")
                else data["academic_period"],
                alert_type=data.get("alert_type"),
                urgency_level=data.get("urgency_level"),
            )
            if errors:
                raise ValueError(errors)

            alert = EarlyAlertRepository.create(
                enrollment=data["enrollment"],
                academic_period=data["academic_period"],
                alert_type=data.get("alert_type"),
                description=data["description"],
                urgency_level=data.get("urgency_level"),
            )
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = alert

    def perform_update(self, serializer):
        """Actualiza la alerta a través del repositorio."""
        data = dict(serializer.validated_data)
        try:
            alert = EarlyAlertRepository.update(serializer.instance.id, **data)
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = alert

    @action(detail=True, methods=["post"])
    def mark_attended(self, request, pk=None):
        """
        Marca una alerta como atendida.

        POST /api/analytics/early-alerts/{id}/mark_attended/
        """
        try:
            alert = self.get_object()
            actions = request.data.get("response_actions", "")
            alert = EarlyAlertService.mark_as_attended(alert.id, request.user.id, actions)
            if alert:
                return ok_response(
                    EarlyAlertSerializer(alert).data,
                    msg="Alerta marcada como atendida",
                )
            return error_response("Alerta no encontrada", status_code=404)
        except Exception as e:
            return error_response(str(e), status_code=400)
