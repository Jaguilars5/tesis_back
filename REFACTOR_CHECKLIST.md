# Checklist de Refactorización — Backend (Layered Pattern)

Basado en la arquitectura del proyecto: `models/` → `repositories/` → `services/` → `api/`.

---

## 1. Estructura del Módulo (por entidad)

```
module_name/                           # ej: school_year, academic_level
  __init__.py                          # Lazy loader con __getattr__
  urls.py                              # InstitutionsRouter + register
  permissions.py                       # ACTION_PERMISSIONS dict
  domain/
    __init__.py
    services.py                        # Business logic (hereda de nada)
    repositories.py                    # Abstract interface (ABC)
  infrastructure/
    __init__.py
    models.py                          # Django Model (TimeStampedModel)
    repositories.py                    # ORM implementation (BaseRepository + Interface)
  application/
    __init__.py
    serializers.py                     # DRF Serializer
    validators.py                      # (opcional) validaciones de negocio
  api/
    __init__.py
    views.py                           # ViewSet (finito, solo llama servicios)
    urls.py                            # (opcional si hay actions extra)
    filters.py                         # (opcional) DjangoFilterBackend filterset
    tests/                             # (opcional, pueden estar en tests/ global)
```

**Archivos que NO deben existir:**

- ❌ `models.py` suelto en la raíz del módulo (debe ir en `infrastructure/`)
- ❌ Query ORM directo en `views.py` o `services.py`
- ❌ Lógica de negocio en `api/views.py`
- ❌ Importaciones circulares entre módulos del mismo app

---

## 2. Modelos (`infrastructure/models.py`)

### Heredar de TimeStampedModel

```python
from apps.core.models import TimeStampedModel

class MyEntity(TimeStampedModel):
    ...
```

- `TimeStampedModel` provee `created_at` y `updated_at` automáticos
- ❌ NO definir `created_at`/`updated_at` manualmente

### is_active

```python
is_active = models.BooleanField(default=True, verbose_name="Activo")
```

- Todas las entidades deben tener campo `is_active`
- El soft-delete del mixin y el filtro `active_only` del repositorio base dependen de él

### app_label

```python
class Meta:
    app_label = "institutions_entity_name"  # único por módulo
    verbose_name = "..."
    verbose_name_plural = "..."
```

### on_delete

- `on_delete=models.PROTECT` para FKs a catálogos o entidades críticas
- `on_delete=models.CASCADE` para relaciones de pertenencia (ej: Section → SchoolYear)
- ❌ NO usar `on_delete=models.SET_NULL` a menos que sea semánticamente correcto

---

## 3. Repositorio — Interface (`domain/repositories.py`)

```python
from abc import ABC, abstractmethod

class EntityRepositoryInterface(ABC):
    @classmethod
    @abstractmethod
    def get_all(cls, active_only=True, search=None): ...
    @classmethod
    @abstractmethod
    def get_by_id(cls, pk): ...
    @classmethod
    @abstractmethod
    def create(cls, **data): ...
    @classmethod
    @abstractmethod
    def update(cls, pk, **data): ...
```

Métodos adicionales según necesidad:

- `get_cascade_counts(cls, instance_id: int) -> dict[str, int]`
- `deactivate_cascade(cls, instance_id: int) -> int`
- Métodos de búsqueda específicos (`get_by_grade`, `get_current`, etc.)
- ❌ NO incluir métodos que no se implementan en infraestructura

---

## 4. Repositorio — Implementación (`infrastructure/repositories.py`)

### Heredar de BaseRepository + Interface

```python
from apps.core.repositories.base import BaseRepository
from ..domain.repositories import EntityRepositoryInterface
from .models import MyEntity

class MyEntityRepository(BaseRepository, EntityRepositoryInterface):
    model = MyEntity
```

### CRUD vía BaseRepository

| Método | Descripción |
|--------|-------------|
| `get_all(active_only=True)` | Filtra `is_active=True` automáticamente si el modelo tiene el campo |
| `get_by_id(pk)` | Retorna None si no existe (no lanza excepción) |
| `create(**data)` | Setea `created_at` y `updated_at` automáticamente |
| `update(pk, **data)` | Setea `updated_at` automáticamente |
| `delete(pk)` | Hard-delete (no soft). Para soft usar `update(is_active=False)` |

### ⚠️ Reglas ORM

- ✅ Toda consulta ORM debe vivir aquí
- ✅ Importar modelos de otros apps solo en `infrastructure/repositories.py` (NO en services ni views)
- ❌ `Model.objects.filter(...)` NO en services, NO en views
- ✅ Usar `cls.model.objects.xxx()` (no el nombre de la clase directamente)
- ✅ Usar `select_related`/`prefetch_related` para optimizar N+1
- ✅ Usar `@transaction.atomic` en operaciones que modifican múltiples tablas

### Patrón cascade

```python
@classmethod
def get_cascade_counts(cls, instance_id: int) -> dict[str, int]:
    child_ids = ChildModel.objects.filter(parent_id=instance_id, is_active=True).values_list("id", flat=True)
    counts = {}
    count = len(child_ids)
    if count:
        counts["nombre plural"] = count
    # ... más niveles si hay árbol
    return counts

@classmethod
@transaction.atomic
def deactivate_cascade(cls, instance_id: int) -> int:
    child_ids = list(ChildModel.objects.filter(parent_id=instance_id, is_active=True).values_list("id", flat=True))
    total = 0
    if child_ids:
        total += ChildModel.objects.filter(id__in=child_ids).update(is_active=False)
    cls.model.objects.filter(pk=instance_id).update(is_active=False)
    return total
```

---

## 5. Servicio (`domain/services.py`)

### Patrón

```python
class MyEntityService:
    repository = MyEntityRepository

    @classmethod
    def get_entity(cls, pk):
        obj = cls.repository.get_by_id(pk)
        if not obj:
            raise ValueError(f"Entidad {pk} no encontrada")
        return obj

    @classmethod
    def create_entity(cls, **kwargs):
        return cls.repository.create(**kwargs)

    @classmethod
    def update_entity(cls, pk, **kwargs):
        cls.get_entity(pk)
        allowed = {"campo1", "campo2", "is_active"}
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(pk, **clean)
```

### soft_delete

```python
@classmethod
def soft_delete(cls, pk, confirm=False):
    obj = cls.get_entity(pk)
    counts = cls.repository.get_cascade_counts(pk)
    total = sum(counts.values())

    if total > 0 and not confirm:
        parts = [f"{v} {k}" for k, v in counts.items()]
        return {
            "requires_confirmation": True,
            "affected_records": total,
            "message": f"Esta acción desactivará {', '.join(parts)} relacionados",
            "id": obj.id,
            "is_active": True,
        }

    total = cls.repository.deactivate_cascade(pk)
    return {
        "id": obj.id,
        "is_active": False,
        "deactivated_records": total,
    }
```

### Reglas

- ✅ Solo lógica de negocio (validaciones, autorización, orchestación)
- ✅ Llamar al repositorio para acceso a datos
- ✅ Usar `@transaction.atomic` para operaciones que modifican múltiples tablas
- ❌ NO queries ORM directas
- ❌ NO importar modelos de otros apps directamente (hacerlo via repositorio)
- ❌ NO lógica de serialización/HTTP

---

## 6. Serializer (`application/serializers.py`)

### Patrón base

```python
from rest_framework import serializers

class MyEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = MyEntity
        fields = "__all__"  # o lista explícita
        read_only_fields = ["created_at", "updated_at"]
```

- ✅ `read_only_fields` incluye `created_at`, `updated_at`
- ❌ NO incluir lógica de negocio en serializers (validaciones complejas van en services/validators)

### FKs: devolver ID + nombre legible

Cuando el modelo tiene una FK, el serializer debe incluir **el ID** (para enviar en create/update) y **el nombre legible** (para mostrar en frontend). El nombre se obtiene vía `source` o `@property` en el modelo.

**Modelo** (`infrastructure/models.py`):
```python
@property
def academic_level_name(self):
    return self.academic_level.name if self.academic_level else None
```

**Serializer** (`application/serializers.py`):
```python
class MyEntitySerializer(serializers.ModelSerializer):
    fk_field_name = serializers.CharField(
        source="fk_field.name", read_only=True
    )

    class Meta:
        model = MyEntity
        fields = "__all__"  # incluye tanto fk_field como fk_field_name
```

- ✅ La FK se envía como `{ "fk_field": <id> }` en POST/PUT
- ✅ La respuesta incluye `{ "fk_field": <id>, "fk_field_name": "Nombre..." }`
- ✅ `fk_field_name` es `read_only=True` (no se envía en entrada)
- ❌ NO duplicar `fk_field_name` en los `fields` del Meta si ya está en `fields = "__all__"` y es una propiedad del modelo
- ❌ NO devolver el objeto FK anidado completo (solo `id` + `name`)

---

## 6.5 Validators (`application/validators.py`)

### Propósito

Centralizar **validaciones de negocio** que van más allá de lo que cubre el serializer (tipos, requeridos, longitud). Ejemplos:

- Fechas inválidas (SchoolYear: `start_date` no puede ser pasada, `end_date` debe ser posterior a `start_date`)
- Unique constraints compuestos que no se pueden expresar en `Meta.unique_together`
- Reglas de integridad referencial (ej: no crear un grado sin subnivel activo)
- Validaciones condicionales (campo A requerido si campo B tiene cierto valor)

### Patrón

Cada validador es una función que retorna `dict` (vacío si pasa, con error si falla). Un `run_all_validators` las ejecuta todas y acumula errores.

```python
"""
Validaciones de negocio para Entity.
"""

def validate_field_not_null(value, field_name):
    if value is None or (isinstance(value, str) and not value.strip()):
        return {field_name: f"{field_name} no puede estar vacío"}
    return {}


def validate_required_fields(data, required):
    """Verifica que todos los campos obligatorios estén presentes y no sean nulos."""
    errors = {}
    for field in required:
        if field not in data or data[field] is None:
            errors[field] = f"{field} es obligatorio"
    return errors


def run_all_validators(**kwargs):
    """Ejecuta todas las validaciones y retorna un diccionario de errores."""
    errors = {}
    errors.update(validate_required_fields(kwargs, ["campo1", "campo2"]))
    # ... más validaciones específicas
    return errors
```

### Uso en el Service

```python
@classmethod
@transaction.atomic
def create_entity(cls, **kwargs):
    errors = validators.run_all_validators(**kwargs)
    if errors:
        raise ValueError(errors)
    return cls.repository.create(**kwargs)
```

### Validaciones comunes por entidad

| Entidad | Validaciones |
|---------|-------------|
| `SchoolYear` | `start_date` no anterior a hoy, `end_date` posterior a `start_date`, sin solapamiento de fechas |
| `AcademicLevel` | `name` requerido, `code` único si se provee |
| `AcademicSublevel` | `code` único (validación DRF + servicio), `academic_level` debe existir y estar activo |
| `AcademicGrade` | `name` requerido, `academic_sublevel` debe existir si se provee |
| `Section` | `parallel` requerido, combinación `(school_year, academic_grade, parallel)` única |

### Reglas

- ✅ Cada validación es una función pura que retorna `dict`
- ✅ `run_all_validators` acumula errores de todas las validaciones
- ✅ El service llama a `run_all_validators` antes de crear/actualizar
- ✅ El ViewSet captura `ValueError` y responde con `ValidationError` HTTP 400
- ❌ NO poner validaciones de negocio en el serializador (solo validación de tipos/requeridos)
- ❌ NO poner validaciones de negocio en el repositorio
- ❌ NO mutar datos dentro de los validadores (solo leer y retornar errores)

---

## 7. ViewSet (`api/views.py`)

### Estructura

```python
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from apps.institutions.api.base import BaseInstitutionsViewSet
from apps.core.utils import ok_response
from ..application.serializers import MyEntitySerializer
from ..domain.services import MyEntityService
from ..infrastructure.repositories import MyEntityRepository
from ..permissions import ACTION_PERMISSIONS


@extend_schema_view(
    list=extend_schema(summary="Listar...", tags=["institutions"]),
    get=extend_schema(summary="Obtener...", tags=["institutions"]),
    create=extend_schema(summary="Crear...", tags=["institutions"]),
    update=extend_schema(summary="Actualizar...", tags=["institutions"]),
    partial_update=extend_schema(summary="Actualizar parcialmente...", tags=["institutions"]),
    destroy=extend_schema(summary="Eliminar...", tags=["institutions"]),
    soft_delete=extend_schema(summary="Desactivar... con cascada", tags=["institutions"]),
)
class MyEntityViewSet(BaseInstitutionsViewSet):
    serializer_class = MyEntitySerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ...
```

### Soft delete endpoint

```python
@action(detail=True, methods=["post"], url_path="soft-delete")
def soft_delete(self, request, pk=None):
    confirm = request.data.get("confirm", False)
    result = MyEntityService.soft_delete(pk, confirm=confirm)
    return ok_response(result)
```

### Filtros por FK y is_active

Cuando el modelo tiene **FKs** o campos que el frontend necesita filtrar, se debe usar `DjangoFilterBackend` con un `filterset_class`.

**Cuándo agregar filtros:**

| Situación | ¿Filtro necesario? |
|-----------|-------------------|
| El frontend necesita listar entidades por FK padre | ✅ Sí, agregar filtro FK |
| El frontend necesita filtrar por `is_active` | ✅ Sí, agregar `is_active` en filterset |
| Solo búsqueda por texto | ❌ No, usar `SearchFilter` |
| Solo ordenamiento | ❌ No, usar `OrderingFilter` |

**Archivo** `api/filters.py`:
```python
import django_filters
from ..infrastructure.models import MyEntity

class MyEntityFilter(django_filters.FilterSet):
    class Meta:
        model = MyEntity
        fields = {
            "name": ["exact", "icontains"],
            "fk_field": ["exact"],
            "is_active": ["exact"],
        }
```

**ViewSet**:
```python
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from .filters import MyEntityFilter

class MyEntityViewSet(BaseInstitutionsViewSet):
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = MyEntityFilter
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code"]
    ordering = ["name"]
```

- ✅ `is_active` debe estar en `filterset_fields` o `filterset_class`
- ✅ Los nombres de los query params coinciden con los campos del modelo (ej: `?academic_level=5`, `?is_active=true`)
- ✅ `SearchFilter` para búsqueda textual (`?search=...`)
- ❌ NO filtrar en cliente (siempre delegar al backend)
- ❌ NO exponer `created_at`/`updated_at` en filterset_fields a menos que sea necesario

### Reglas generales

- ✅ Heredar de `BaseInstitutionsViewSet` (que incluye `SoftDeleteModelMixin`)
- ✅ ViewSet FINO: solo recibe request, llama servicio, retorna respuesta
- ✅ Usar `ok_response()` / `error_response()` de `apps.core.utils`
- ✅ `action_permissions` definido en `permissions.py`
- ❌ NO queries ORM directas
- ❌ NO lógica de negocio
- ❌ NO importar modelos directamente
- ❌ NO `@api_view` functions (siempre ViewSets)
- ❌ `perform_destroy` sin override a menos que haga soft-delete explícito

---

## 8. Rutas (`urls.py`)

```python
from apps.institutions.api.routers import InstitutionsRouter
from .api.views import MyEntityViewSet

router = InstitutionsRouter()
router.register(r"entity-url", MyEntityViewSet, basename="entity-name")

urlpatterns = router.urls
```

- ✅ `InstitutionsRouter` genera: list, create, get, update, partial_update, destroy + dynamic routes
- ✅ `routers.py` de `api/base.py` es compartido, NO crear otro
- ❌ NO funciones sueltas en `urlpatterns`

---

## 9. Permisos (`permissions.py`)

```python
from apps.core.constants.permissions import institutions

ACTION_PERMISSIONS = {
    "list": institutions.VIEW_ENTITY,
    "get": institutions.VIEW_ENTITY,
    "create": institutions.CREATE_ENTITY,
    "update": institutions.UPDATE_ENTITY,
    "partial_update": institutions.UPDATE_ENTITY,
    "destroy": institutions.DELETE_ENTITY,
    "soft_delete": institutions.DELETE_ENTITY,
}
```

- ✅ Usar constantes de `apps.core.constants.permissions`
- ✅ Formato: `modulo.accion` (ej: `grading.create_note`)
- ❌ NO strings hardcodeados
- ❌ NO `None` como permiso (si es público, manejarlo aparte)

---

## 10. Lazy Loader (`__init__.py` del módulo)

```python
__all__ = ["MyEntity", "MyEntityRepository", "MyEntityService"]

def __getattr__(name):
    if name == "MyEntity":
        from .infrastructure.models import MyEntity
        return MyEntity
    if name == "MyEntityRepository":
        from .infrastructure.repositories import MyEntityRepository
        return MyEntityRepository
    if name == "MyEntityService":
        from .domain.services import MyEntityService
        return MyEntityService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
```

---

## 11. Tests

### Configuración

- Usar `--settings=config.settings.test`
- `TestCase` de Django + `APIClient` de DRF (NO pytest)
- `force_authenticate(user=...)` para auth (NO JWT)
- Fixtures manuales en `setUp()` (NO factory libraries)

### Estructura

```python
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

class MyEntityAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()  # o crear manual
        self.client.force_authenticate(user=self.user)

    def test_list_empty(self):
        response = self.client.get("/api/institutions/entity-url/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
```

### Qué testear

- [ ] CRUD básico (list, create, get, update, destroy)
- [ ] Soft-delete (sin confirm → requiere confirmación, con confirm → desactiva)
- [ ] Soft-delete cascada (verificar que hijos se desactivan)
- [ ] Permisos (usuario sin permiso recibe 403)
- [ ] Paginación
- [ ] Búsqueda y filtros
- [ ] Validaciones de negocio (errores 400)

---

## 12. API Response Contract

Todas las respuestas siguen el formato global:

```json
// Éxito
{"ok": true, "data": {...}, "msg": "..."}

// Error
{"ok": false, "data": null, "msg": "..."}
```

- ✅ Usar `ok_response(data, msg="...")` y `error_response(msg)` de `apps.core.utils`
- ✅ El renderer global `StandardResponseRenderer` aplica automáticamente
- ✅ Paginación: metadata dentro de `data`

---

## 13. Convenciones de Código

### Nombres

- Modelos: `CamelCase` (convención histórica del proyecto)
- Métodos/variables: `snake_case`
- Permisos: `modulo.accion` (ej: `institutions.view_school_year`)
- URL endpoints: `kebab-case` (ej: `school-year`, `academic-levels`)

### Imports

```python
# Primero: built-in
from datetime import date

# Segundo: Django/DRF
from django.db import transaction
from rest_framework.decorators import action

# Tercero: apps del proyecto
from apps.core.utils import ok_response
from apps.institutions.api.base import BaseInstitutionsViewSet

# Cuarto: relativo del módulo
from ..application.serializers import MyEntitySerializer
```

- ❌ NO importar modelos de otros apps desde services o views
- ✅ Solo `infrastructure/repositories.py` puede importar modelos de otros apps

### Strings de verbose

- Usar `\uXXXX` escapes solo si es necesario (el archivo ya los tiene)
- Preferir caracteres literales UTF-8 cuando el editor lo soporte

---

## 14. OpenAPI / Schema

- `drf-spectacular` genera schema automáticamente desde los ViewSets
- `@extend_schema_view` documenta cada acción
- `soft_delete=extend_schema(...)` debe incluirse en `@extend_schema_view`
- Validar schema:
  ```bash
  python manage.py spectacular --settings=config.settings.local --validate
  ```

---

## 15. Audit Final

### Estructura y capas

- [ ] `models.py` está en `infrastructure/` (no en la raíz del módulo)
- [ ] Repositorio interface en `domain/repositories.py`
- [ ] Repositorio impl en `infrastructure/repositories.py`
- [ ] Servicio en `domain/services.py`
- [ ] Serializer en `application/serializers.py`
- [ ] ViewSet en `api/views.py`
- [ ] `__init__.py` con lazy loader
- [ ] `urls.py` con router.register

### ORM

- [ ] Sin `Model.objects.filter()` en views
- [ ] Sin `Model.objects.filter()` en services
- [ ] Sin importaciones de modelos de otros apps en services/views
- [ ] `get_cascade_counts` y `deactivate_cascade` en repositorio (no en service ni view)

### Soft Delete

- [ ] Modelo tiene campo `is_active`
- [ ] `SoftDeleteModelMixin` en `BaseInstitutionsViewSet`
- [ ] `soft_delete` action en ViewSet llama al servicio
- [ ] Servicio `soft_delete` maneja confirmación y cascada
- [ ] Repositorio implementa `get_cascade_counts` y `deactivate_cascade`
- [ ] `perform_destroy` solo sobreescrito si hace soft-delete (SchoolYear) o hard-delete
- [ ] La ruta `POST /soft-delete/` existe y funciona

### Response

- [ ] Usa `ok_response()` / `error_response()`
- [ ] Formato `{"ok": bool, "data": ..., "msg": "..."}`
- [ ] Códigos HTTP correctos (201 en create, 200 en éxito, 400/403/404/409 en errores)
- [ ] Paginación con `StandardResultsSetPagination`

### Permisos

- [ ] `action_permissions` definido con constantes de `apps.core.constants.permissions`
- [ ] Sin strings hardcodeados
- [ ] `soft_delete` tiene permiso asignado (generalmente `DELETE`)
- [ ] Superusuarios bypassan verificación

### Tests

- [ ] Test de listado (vacio y con datos)
- [ ] Test de creación
- [ ] Test de actualización
- [ ] Test de soft-delete (sin confirm → confirm, con confirm → desactiva)
- [ ] Test de cascada (verificar hijos desactivados)
- [ ] Test de permisos (403 sin permiso)
- [ ] Test de validación (400 con datos inválidos)
- [ ] Usa `--settings=config.settings.test`
- [ ] Usa `force_authenticate` (no JWT)
- [ ] Sin pytest, sin factory libraries

### Validators

- [ ] `application/validators.py` existe
- [ ] `run_all_validators()` acumula errores de todas las validaciones
- [ ] Service llama a `run_all_validators()` antes de crear/actualizar
- [ ] ViewSet captura `ValueError` y responde con `ValidationError` HTTP 400
- [ ] Validaciones de campos obligatorios (no nulos, no vacíos)
- [ ] Validaciones específicas de negocio (fechas, unicidad compuesta, etc.)
- [ ] Sin validaciones de negocio en el serializer
- [ ] Sin validaciones de negocio en el repositorio

### FK name en serializer

- [ ] Modelo tiene `@property` por cada FK legible (`fk_field_name`)
- [ ] Serializer incluye `fk_field_name = CharField(source=..., read_only=True)`
- [ ] Response devuelve `{ "fk_field": <id>, "fk_field_name": "Nombre..." }`
- [ ] `fk_field_name` es `read_only=True`

### Filters

- [ ] `filter_backends` configurados si aplica
- [ ] `filterset_class` o `filterset_fields` si usa `DjangoFilterBackend`
- [ ] `search_fields` si usa `SearchFilter`
- [ ] `is_active` incluido en filterset si el modelo lo tiene
- [ ] FKs padre incluidos en filterset (ej: `academic_level`, `school_year`)
- [ ] Los nombres de query params coinciden con campos del modelo
- [ ] `ordering_fields` y `ordering` definidos en ViewSet
- [ ] `@extend_schema_view` documenta todas las acciones incluyendo `soft_delete`
- [ ] Schema OpenAPI válido (`python manage.py spectacular --validate`)
