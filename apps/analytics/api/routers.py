"""
Router personalizado para el módulo Analytics.

Igual que AcademicRouter, usa 'get' en lugar de 'retrieve' para consistencia
con BaseAnalyticsViewSet.
"""

from rest_framework.routers import DefaultRouter, Route, DynamicRoute


class AnalyticsRouter(DefaultRouter):
    """
    Router que mapea GET /{id}/ a la acción 'get' en lugar de 'retrieve'.

    Esto mantiene consistencia con los permisos action_permissions donde
    se usa 'get' para lectura de instancia individual.
    """

    routes = [
        Route(
            url=r"^{prefix}{trailing_slash}$",
            mapping={
                "get": "list",
                "post": "create",
            },
            name="{basename}-list",
            detail=False,
            initkwargs={"suffix": "List"},
        ),
        DynamicRoute(
            url=r"^{prefix}/{url_path}{trailing_slash}$",
            name="{basename}-{url_name}",
            detail=False,
            initkwargs={},
        ),
        Route(
            url=r"^{prefix}/{lookup}{trailing_slash}$",
            mapping={
                "get": "get",
                "put": "update",
                "delete": "destroy",
            },
            name="{basename}-detail",
            detail=True,
            initkwargs={"suffix": "Instance"},
        ),
        DynamicRoute(
            url=r"^{prefix}/{lookup}/{url_path}{trailing_slash}$",
            name="{basename}-{url_name}",
            detail=True,
            initkwargs={},
        ),
    ]
