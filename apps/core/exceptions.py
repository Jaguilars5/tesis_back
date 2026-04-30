from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    """
    Manejador de excepciones personalizado para asegurar que los errores
    también sigan el formato {ok, data, msg}.
    """
    response = exception_handler(exc, context)

    if response is not None:
        # Ya es una respuesta de DRF, la reformateamos
        response.data = {
            'ok': False,
            'data': response.data,
            'msg': str(exc)
        }
    else:
        # Errores no controlados (500)
        # En producción podrías querer loguear esto en Sentry
        return Response({
            'ok': False,
            'data': {},
            'msg': f"Error interno del servidor: {str(exc)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
