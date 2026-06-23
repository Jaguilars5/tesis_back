from rest_framework.decorators import action

from apps.core.utils import ok_response, error_response


class SoftDeleteModelMixin:
    @action(detail=True, methods=["post"], url_path="soft-delete")
    def soft_delete(self, request, pk=None):
        instance = self.get_object()
        if hasattr(instance, "is_active"):
            instance.is_active = False
            instance.save(update_fields=["is_active"])
            return ok_response({"id": instance.id, "is_active": False})
        return error_response("Este modelo no soporta borrado lógico")
