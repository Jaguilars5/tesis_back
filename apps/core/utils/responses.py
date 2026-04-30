from rest_framework.response import Response

def ok_response(data, status=200):
    """
    Retorna una respuesta exitosa estandarizada con código de estado opcional.
    """
    return Response({'ok': True, 'data': data, 'msg': ''}, status=status)

def error_response(msg, status=400):
    """
    Retorna una respuesta de error estandarizada.
    """
    return Response({'ok': False, 'data': {}, 'msg': str(msg)}, status=status)
