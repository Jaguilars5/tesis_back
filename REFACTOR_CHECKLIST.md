# Checklist de Refactorización — Backend (Layered Pattern)

Basado en la arquitectura del proyecto: `models/` → `repositories/` → `services/` → `api/`.

> ⚠️ **No todas las entidades son iguales.** Este checklist históricamente asumía un único
> tipo de entidad (catálogo con CRUD + soft-delete en cascada). En la práctica el dominio
> tiene **5 arquetipos** con semánticas distintas para `is_active`, soft-delete, operaciones
> CRUD y separación en submódulos. **Antes de auditar/refactorizar un módulo, identifica su
> arquetipo en la sección 0** y aplica solo el tratamiento que le corresponde. Cada sección
> de este documento indica con etiquetas `[A1] [A2] [A3] [A4] [A5]` a qué arquetipos aplica.

---

## 0. Arquetipos de Entidad (determina qué tratamiento aplica)

El primer paso de cualquier refactor es clasificar la entidad. El arquetipo decide si lleva
`is_active`, si soporta soft-delete, qué operaciones CRUD expone y si va en submódulo propio.

### A1 — Catálogo / Dato maestro

Entidades de configuración que el usuario gestiona (alta/baja/edición). **Este es el caso para
el que se escribió el resto del checklist.**

- Ejemplos: `SchoolYear`, `AcademicLevel`, `AcademicSublevel`, `AcademicGrade`, `Section`,
  `PeriodType`, `Subject`, `AttendanceStatus`, `AbsenceType`, `IncidentType`, `Severity`,
  `ActivityType`, `QualitativeScale`.
- Herencia: `TimeStampedModel` (sin `SyncableModel`).
- `is_active`: ✅ **obligatorio**.
- Soft-delete: ✅ con cascada (`get_cascade_counts` + `deactivate_cascade`).
- CRUD: completo (list, get, create, update, destroy→soft, `soft-delete`).
- Base ViewSet: `Base<App>ViewSet` (catálogo estándar).
- Submódulo por entidad: ✅.

### A2 — Registro transaccional / Evento (Syncable)

Hechos registrados en el tiempo, normalmente sincronizables desde móvil offline-first. **No se
borran: se anulan o se corrige su estado.**

- Ejemplos: `Attendance`, `ConductIncident`, `StudentNote`.
- Herencia: `TimeStampedModel` **+ `SyncableModel`** (tiene `uuid` + `sync_status`).
- `is_active`: ❌ **no lleva** (se removió a propósito; usar anulación / cambio de estado).
- Soft-delete: ❌. `DELETE` debe responder `405` (lo hace `SoftDestroyMixin` al no haber `is_active`).
- CRUD: **C / R / U** (sin `destroy`). Corrección vía anulación (`manually_overridden`,
  cambio de `attendance_status`, etc.) y registro en historial (A3) cuando aplique.
- ViewSet: recortar `http_method_names` quitando `delete` y **NO** declarar `destroy`/`soft_delete`
  en `@extend_schema_view`.
- Submódulo por entidad: ✅.

### A3 — Historial / Auditoría inmutable (append-only)

Registros que solo se agregan y se leen; nunca se editan ni se borran.

- Ejemplos: `GradeChangeHistory` (y logs de auditoría en general).
- Herencia: `TimeStampedModel` (suele tener su propio `*_at = auto_now_add` + `ordering` desc).
- `is_active`: ❌ no aplica.
- Soft-delete: ❌. Sin `update`, sin `destroy`.
- CRUD: **solo R** (Read). La escritura la hace el sistema (no el usuario) al ocurrir el evento.
- ViewSet: `ReadOnlyModelViewSet` (o un `BaseReadOnlyViewSet` compartido). Esto **es correcto**,
  no una desviación del patrón.
- Submódulo: vive junto a la entidad que audita (no necesita app propia).

### A4 — Agregado derivado / Calculado

Resultados de un cálculo o agregación; se **recalculan/reemplazan**, no se borran a mano.

- Ejemplos: `PeriodGradeSummary`, `BehaviorEvaluation`, snapshots/scores de `analytics`.
- Herencia: `TimeStampedModel` (con `calculated_at`, `calculated_by`, unique constraint del
  grano de cálculo).
- `is_active`: ❌ no aplica.
- Soft-delete: ❌. Se sustituye por **upsert idempotente** (`get_or_create` + acción `recalculate`).
- CRUD: **R + recalculate**. Sin `destroy` ni `soft-delete`.
- ViewSet: base estándar pero **sin** `destroy`/`soft_delete` en `http_method_names` ni en el schema;
  añade `@action recalculate`.
- Submódulo por entidad: ✅.

### A5 — Raíz de agregado / Identidad

Dominios ricos centrados en una o pocas raíces (no una colección de catálogos independientes).

- Ejemplos: `User` (iam), `Person` (people), `Student`/`Enrollment` (students), `SyncQueue` (integration).
- `is_active`: depende (p.ej. `User.is_active` sí; otros usan `status`).
- Soft-delete: caso a caso (no asumir cascada de catálogo).
- CRUD: completo, frecuentemente con acciones de dominio extra (activar, cambiar rol, matricular…).
- Submódulo por entidad: ❌ **no obligatorio**. Una estructura de capas plana
  (`domain/`, `application/`, `infrastructure/`, `api/` sin sub-apps por entidad) es aceptable;
  forzar "submódulo por entidad" aquí es sobre-ingeniería.

### Árbol de decisión

```
¿La entidad es resultado de un cálculo/agregación?           → A4 (recalcular, sin is_active)
¿Es un log que solo se agrega y se lee (auditoría)?          → A3 (ReadOnly, sin is_active)
¿Es un hecho/evento en el tiempo (hereda SyncableModel)?     → A2 (sin is_active, DELETE=405)
¿Es una raíz de identidad/dominio rico (User, Person...)?    → A5 (capas planas, caso a caso)
En cualquier otro caso (config que el usuario administra)    → A1 (catálogo: CRUD + soft-delete)
```

### Matriz resumen

| Dimensión | A1 Catálogo | A2 Transaccional | A3 Historial | A4 Calculado | A5 Identidad |
|---|:--:|:--:|:--:|:--:|:--:|
| `is_active` | ✅ obligatorio | ❌ | ❌ | ❌ | depende |
| Soft-delete cascada | ✅ | ❌ | ❌ | ❌ | caso a caso |
| `DELETE` → 405 | n/a (hace soft) | ✅ | ✅ | ✅ | caso a caso |
| Operaciones CRUD | C R U + soft-del | C R U | **R** | R + recalculate | C R U + acciones |
| Hereda `SyncableModel` | ❌ | ✅ | ❌ | a veces | ❌ |
| Submódulo por entidad | ✅ | ✅ | ✅ (junto a su raíz) | ✅ | ❌ (plano OK) |
| Base ViewSet | `Base<App>ViewSet` | base con `http_method_names` recortado | `ReadOnly` | base + `recalculate` | propio |

> **Regla de oro:** las secciones 1–15 de este documento describen el tratamiento **A1**.
> Para A2–A5 aplica solo lo que la matriz y las etiquetas `[Ax]` permitan; lo demás NO es una
> inconsistencia a "corregir hacia catálogo".

---

## 1. Estructura del Módulo (por entidad) `[A1] [A2] [A3] [A4]` · *plano permitido en* `[A5]`

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
- `[A2]` Los registros transaccionales/sincronizables heredan **además** de `SyncableModel`
  (`apps.integration.models.syncable_mixin`), que aporta `uuid` + `sync_status`:
  `class Attendance(TimeStampedModel, SyncableModel): ...`

### is_active `[A1]` · *opcional en* `[A5]` · ❌ *NO en* `[A2] [A3] [A4]`

```python
is_active = models.BooleanField(default=True, verbose_name="Activo")
```

- Solo las entidades **A1 (catálogo)** deben tener `is_active` obligatorio. El soft-delete del
  mixin y el filtro `active_only` del repositorio base dependen de él.
- **A2 (transaccional), A3 (historial) y A4 (calculado) NO llevan `is_active`** — usan anulación,
  son inmutables o se recalculan. Si ves un modelo Syncable/transaccional sin `is_active`, **es
  correcto**, no lo agregues.
- **A5 (identidad)**: depende de la entidad (`User.is_active` sí; otros pueden usar `status`).

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

### soft_delete `[A1]` · *en* `[A2] [A3] [A4]` *usar el equivalente del arquetipo*

> Solo los catálogos (A1) implementan `soft_delete` con cascada. Para los demás arquetipos el
> método de "baja" cambia: **A2** → `anular`/cambio de estado (registra historial), **A3** → no
> existe (inmutable), **A4** → `recalculate` (reemplaza el cálculo, no desactiva).

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

> **Selección de base/operaciones según arquetipo** (ver sección 0):
>
> | Arquetipo | Base ViewSet | `http_method_names` | `@extend_schema_view` incluye | Acción extra |
> |---|---|---|---|---|
> | A1 Catálogo | `Base<App>ViewSet` | todos | `destroy`, `soft_delete` | `soft_delete` |
> | A2 Transaccional | `Base<App>ViewSet` | sin `delete` | **NO** `destroy`/`soft_delete` | `anular`/estado |
> | A3 Historial | `ReadOnlyModelViewSet` | solo `get`/`head`/`options` | solo `list`, `get` | — |
> | A4 Calculado | `Base<App>ViewSet` | sin `delete` | **NO** `destroy`/`soft_delete` | `recalculate` |
> | A5 Identidad | propio | según dominio | según dominio | acciones de dominio |
>
> ❗ Error común detectado en auditoría: declarar `destroy`/`soft_delete` en `@extend_schema_view`
> de una entidad A2/A4 (sin `is_active`). El schema anuncia un borrado que en runtime devuelve
> `405`. Para A2/A4 **no** declares esas acciones y recorta `http_method_names`.

### Estructura `[A1]` (catálogo; ver tabla anterior para A2–A5)

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

### Soft delete endpoint `[A1]`

```python
@action(detail=True, methods=["post"], url_path="soft-delete")
def soft_delete(self, request, pk=None):
    confirm = request.data.get("confirm", False)
    result = MyEntityService.soft_delete(pk, confirm=confirm)
    return ok_response(result)
```

### Endpoint de baja por arquetipo (alternativas a `soft-delete`)

```python
# [A2] Transaccional: anular sin borrar (registra historial / cambia estado)
@action(detail=True, methods=["post"], url_path="anular")
def anular(self, request, pk=None):
    result = MyEntityService.anular(pk, user_id=request.user.id, reason=request.data.get("reason"))
    return ok_response(result)

# [A4] Calculado: recalcular (upsert idempotente, NO desactiva)
@action(detail=True, methods=["post"], url_path="recalculate")
def recalculate(self, request, pk=None):
    result = MyEntityService.recalculate(pk)
    return ok_response(result)

# [A2][A4] Bloquear DELETE explícitamente
http_method_names = ["get", "post", "put", "patch", "head", "options"]  # sin "delete"

# [A3] Historial: solo lectura
class MyHistoryViewSet(ReadOnlyModelViewSet):  # list + retrieve únicamente
    ...
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

### Qué testear (según arquetipo)

`[A1]` Catálogo:
- [ ] CRUD básico (list, create, get, update, destroy)
- [ ] Soft-delete (sin confirm → requiere confirmación, con confirm → desactiva)
- [ ] Soft-delete cascada (verificar que hijos se desactivan)

`[A2]` Transaccional:
- [ ] Create/Read/Update; `DELETE` responde `405`
- [ ] Anulación / cambio de estado (no borra el registro)
- [ ] Sincronización (`sync_status`) si aplica

`[A3]` Historial:
- [ ] Solo lectura (list/get); `POST`/`PUT`/`DELETE` no expuestos
- [ ] El historial se genera al ocurrir el evento de origen

`[A4]` Calculado:
- [ ] `recalculate` es idempotente (no duplica por unique constraint)
- [ ] `DELETE`/`soft-delete` no expuestos

Transversal (todos los arquetipos):
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
- `soft_delete=extend_schema(...)` se incluye en `@extend_schema_view` **solo para A1 (catálogo)**.
  Para A2/A4 **no** declarar `destroy`/`soft_delete` (no existen → el schema no debe anunciarlos).
  Para A3 declarar únicamente `list` y `get`.
- Validar schema:
  ```bash
  python manage.py spectacular --settings=config.settings.local --validate
  ```

---

## 15. Audit Final

> **Paso 0 — Identifica el arquetipo (sección 0) antes de marcar nada.** Las casillas de
> "Soft Delete" y `is_active` aplican **solo a A1**. Para A2–A5 usa el bloque "Por arquetipo".

### Por arquetipo (marcar el que corresponda)

- [ ] **A1 Catálogo** — tiene `is_active`, soft-delete con cascada, CRUD completo.
- [ ] **A2 Transaccional** — hereda `SyncableModel`, sin `is_active`, `DELETE`=405, acción de anulación/estado, sin `destroy`/`soft_delete` en schema.
- [ ] **A3 Historial** — `ReadOnlyModelViewSet`, append-only, sin `update`/`destroy`/`is_active`.
- [ ] **A4 Calculado** — sin `is_active`, acción `recalculate` idempotente, sin `destroy`/`soft_delete`.
- [ ] **A5 Identidad** — capas planas permitidas (sin submódulo por entidad), soft-delete caso a caso.

### Estructura y capas

- [ ] `models.py` está en `infrastructure/` (no en la raíz del módulo) *(plano permitido en A5)*
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
- [ ] `[A1]` `get_cascade_counts` y `deactivate_cascade` en repositorio (no en service ni view)

### Soft Delete `[A1]` — *omitir por completo en A2/A3/A4; caso a caso en A5*

- [ ] Modelo tiene campo `is_active`
- [ ] `SoftDeleteModelMixin` en `BaseInstitutionsViewSet`
- [ ] `soft_delete` action en ViewSet llama al servicio
- [ ] Servicio `soft_delete` maneja confirmación y cascada
- [ ] Repositorio implementa `get_cascade_counts` y `deactivate_cascade`
- [ ] `perform_destroy` solo sobreescrito si hace soft-delete (SchoolYear) o hard-delete
- [ ] La ruta `POST /soft-delete/` existe y funciona

### Baja / Inmutabilidad `[A2] [A3] [A4]`

- [ ] **A2**: modelo NO tiene `is_active`; `http_method_names` sin `delete`; `DELETE` responde `405`; existe acción de anulación/cambio de estado; el historial (A3) se registra si aplica.
- [ ] **A3**: ViewSet es `ReadOnly`; no expone `create`/`update`/`destroy`; no tiene `is_active`.
- [ ] **A4**: modelo NO tiene `is_active`; existe `recalculate` idempotente (respeta unique constraint); no expone `destroy`/`soft_delete`.
- [ ] El `@extend_schema_view` NO anuncia acciones inexistentes para el arquetipo.

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
