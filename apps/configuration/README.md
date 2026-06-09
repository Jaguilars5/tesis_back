# Módulo `configuration` — Configuración del Sistema

## Descripción
Almacena pares clave-valor para opciones globales del sistema.

## Modelos
- **SystemConfig** — Configuración clave-valor (key=PK, value, description)

## API Endpoints (`/api/configuration/`)
- `system-config/` — CRUD de configuraciones

## Servicios
- `ConfigService` — get/set de configuraciones con validación

## Repositorios
- `ConfigRepository` — CRUD + get_or_create

## Tests
- 15 tests (modelos, API, permisos RBAC)

## Dependencias
- Ninguna (app independiente)
