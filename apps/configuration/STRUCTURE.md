# Módulo `configuration` — Estructura

## Árbol de archivos

```
configuration/
├── __init__.py
├── apps.py
├── urls.py                     # Router: system-config
├── README.md
│
├── models/
│   ├── __init__.py
│   └── system_config.py        # SystemConfig (key, value, description)
│
├── repositories/
│   ├── __init__.py
│   └── config_repository.py    # ConfigRepository (CRUD + get_or_create)
│
├── services/
│   ├── __init__.py
│   └── config_service.py       # ConfigService (get, set, get_all)
│
├── api/
│   ├── __init__.py
│   ├── README.md
│   ├── serializers.py          # SystemConfigSerializer
│   └── views.py                # SystemConfigViewSet (CRUD)
│
└── tests/
    ├── __init__.py
    ├── test_api.py
    ├── test_api_permissions.py
    └── test_models.py
```

## Serializers

| Serializer | Modelo |
|------------|--------|
| `SystemConfigSerializer` | SystemConfig (fields: all) |

## Workflow

```
ConfigService.set("KEY", "value") → ConfigRepository.get_or_create → SystemConfig
ConfigService.get("KEY") → ConfigRepository.get_by_id → value
```

## Guía de imports

```python
from apps.configuration.models import SystemConfig
from apps.configuration.services.config_service import ConfigService
from apps.configuration.api.views import SystemConfigViewSet
```
