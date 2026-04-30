from rest_framework.renderers import JSONRenderer

class StandardResponseRenderer(JSONRenderer):
    """
    Renderer que asegura que todas las respuestas JSON tengan el formato:
    {
        "ok": bool,
        "data": mixed,
        "msg": string
    }
    """
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response')
        
        # Si ya tiene el formato esperado, no lo modificamos
        if isinstance(data, dict) and all(k in data for k in ('ok', 'data', 'msg')):
            return super().render(data, accepted_media_type, renderer_context)

        # Si es una respuesta de error de DRF (e.g. validación)
        is_error = response.status_code >= 400
        
        formatted_data = {
            'ok': not is_error,
            'data': data if not is_error else {},
            'msg': '' if not is_error else str(data)
        }
        
        # Si es un error de validación (dict con detalles), lo movemos a msg o data.errors
        if is_error and isinstance(data, dict):
            formatted_data['msg'] = "Error de validación o proceso."
            formatted_data['data'] = data

        return super().render(formatted_data, accepted_media_type, renderer_context)
