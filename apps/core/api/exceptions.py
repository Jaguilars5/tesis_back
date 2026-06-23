from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def _extract_first_error(data):
    """Extrae el primer mensaje de error legible de un dict de errores DRF."""
    if not isinstance(data, dict):
        return str(data)
    for field, errors in data.items():
        if isinstance(errors, list) and errors:
            return str(errors[0])
        if isinstance(errors, str):
            return errors
    return str(data)


def custom_exception_handler(exc, context):
    """
    Manejador de excepciones personalizado para asegurar que los errores
    también sigan el formato {ok, data, msg}.
    """
    response = exception_handler(exc, context)

    if response is not None:
        data = response.data
        if isinstance(exc, ValidationError) and isinstance(data, dict):
            msg = _extract_first_error(data)
            response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        else:
            msg = str(exc)
        response.data = {
            "ok": False,
            "data": data,
            "msg": msg,
        }
    else:
        # Errores no controlados (500)
        return Response(
            {
                "ok": False,
                "data": {},
                "msg": f"Error interno del servidor: {str(exc)}",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response
