from rest_framework.decorators import action
from rest_framework import status

from apps.core.utils import ok_response, error_response


class SoftDestroyMixin:
    """
    Mixin que convierte el DELETE estándar (destroy) en baja lógica.

    - Si el modelo tiene is_active -> lo pone en False (soft delete)
    - Si no tiene is_active -> devuelve 405 (usar anulación/cambio de estado)

    Esto evita el borrado físico por defecto en todos los ViewSets.
    """

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if hasattr(instance, "is_active"):
            instance.is_active = False
            instance.save(update_fields=["is_active"])
            return ok_response(
                {"id": instance.id, "is_active": False},
                msg="Desactivado exitosamente",
            )
        return error_response(
            "Este recurso no permite eliminación física. "
            "Use la acción de anulación o cambio de estado correspondiente.",
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


class SoftDeleteModelMixin:
    @action(detail=True, methods=["post"], url_path="soft-delete")
    def soft_delete(self, request, pk=None):
        instance = self.get_object()
        if hasattr(instance, "is_active"):
            instance.is_active = False
            instance.save(update_fields=["is_active"])
            return ok_response({"id": instance.id, "is_active": False})
        return error_response("Este modelo no soporta borrado lógico")
