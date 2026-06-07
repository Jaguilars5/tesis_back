import copy

from drf_spectacular.openapi import AutoSchema
from drf_spectacular.plumbing import build_basic_type
from drf_spectacular.types import OpenApiTypes


class StandardResponseAutoSchema(AutoSchema):
    """AutoSchema que envuelve todas las respuestas 2xx en el formato estándar {ok, data, msg}."""

    def _get_response_bodies(self, direction='response'):
        bodies = super()._get_response_bodies(direction)
        wrapped = {}
        for status_code, body in bodies.items():
            if status_code.startswith('2') and 'content' in body:
                content = {}
                for media_type, media_obj in body['content'].items():
                    if media_type == 'application/json' and 'schema' in media_obj:
                        original = media_obj['schema']
                        media_obj = copy.deepcopy(media_obj)
                        media_obj['schema'] = {
                            'type': 'object',
                            'properties': {
                                'ok': {'type': 'boolean', 'description': 'Indica si la operación fue exitosa'},
                                'data': original,
                                'msg': {'type': 'string', 'description': 'Mensaje informativo o de error'},
                            },
                            'required': ['ok', 'data', 'msg'],
                        }
                    content[media_type] = media_obj
                body = {**body, 'content': content}
            wrapped[status_code] = body
        return wrapped
