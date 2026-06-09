# Estructura de Configuration

## models/
- `system_config.py` — SystemConfig (key-value store)

## api/
- `SystemConfigViewSet` — CRUD completo

## services/
- `config_service.py` — ConfigService (get/set)

## repositories/
- `config_repository.py` — ConfigRepository (CRUD + get_or_create)

## tests/ (15 tests)
- `test_models.py`, `test_api.py`, `test_api_permissions.py`
