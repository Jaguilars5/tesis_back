# Estructura del Módulo Grading

```
grading/
├─ api/                          # REST API
│  ├─ __init__.py
│  ├─ serializers.py             # Serializers (Note, Attendance, Incident)
│  ├─ urls.py                    # Rutas dinámicas
│  └─ views.py                   # Generador de vistas CRUD
│
├─ models/                       # Capa de datos
│  ├─ __init__.py                # Re-export de modelos
│  ├─ student_note.py            # StudentNote
│  ├─ attendance.py              # Attendance
│  └─ conduct_incident.py        # ConductIncident
│
├─ repositories/                 # Capa de acceso a datos
│  ├─ __init__.py
│  └─ grading_repo.py            # Repositorios especializados (3)
│
├─ services/                     # Capa de lógica de negocio
│  ├─ __init__.py
│  └─ grading_service.py         # Lógica centralizada
│
├─ tests/                        # Verificación
│  ├─ __init__.py
│  └─ ...
│
├─ __init__.py                   # Paquete Python
├─ admin.py                      # Panel Django
├─ apps.py                       # Configuración de app
├─ README.md                     # Documentación principal
├─ urls.py                       # Inclusión de api/urls.py
└─ migrations/                   # Auto-generadas
```

## Organización por Responsabilidades

### 🗄️ Capa de Datos

- **models/**: Define el esquema de la base de datos y validaciones de campo.
- **repositories/**: Abstrae las consultas ORM. Ningún otro componente debe usar `Model.objects` directamente.

### 💼 Capa de Lógica

- **services/**: Implementa las reglas de negocio, cálculos y orquestación entre modelos.
- **tests/**: Garantiza la integridad de la lógica.

### 🌐 Capa HTTP

- **api/**: Maneja la entrada/salida de datos vía HTTP.
- **admin.py**: Configura la interfaz visual para administradores.

## ¿Dónde agregar cosas nuevas?

| Necesidad         | Carpeta         | Archivo                    |
| ----------------- | --------------- | -------------------------- |
| Nuevo modelo      | `models/`       | `nuevo_modelo.py`          |
| Query compleja    | `repositories/` | `grading_repo.py`          |
| Lógica de negocio | `services/`     | `grading_service.py`       |
| Endpoint API      | `api/`          | `views.py`                 |
| Serializer        | `api/`          | `serializers.py`           |
| Test              | `tests/`        | `test_{tipo}.py`           |

## Niveles de Importación

### ✅ Correcto

```python
# Desde otra app
from apps.grading.models import StudentNote
from apps.grading.services.grading_service import GradingService

# Dentro del módulo grading
from .models import StudentNote
from .repositories.grading_repo import StudentNoteRepository
```

### ❌ Incorrecto

```python
# Evitar importar de archivos internos si hay re-export en __init__.py
from apps.grading.models.student_note import StudentNote  # Usa models/__init__.py
```

## Re-exports

La carpeta **models/** re-exporta sus contenidos en `__init__.py`:

```python
from apps.grading.models import StudentNote, Attendance, ConductIncident
```

Esto permite importaciones más limpias y consistentes con el estándar del proyecto.
