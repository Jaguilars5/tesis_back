# Estructura Técnica: Módulo `accounts`

Este documento detalla la organización interna y las responsabilidades de cada componente dentro del módulo de gestión de identidad.

## Árbol de Directorios

```text
accounts/
├── api/                  # Capa de Entrada (REST)
│   ├── serializers.py    # Definición de esquemas JSON
│   ├── views.py          # Controladores (ViewSets)
│   ├── filters.py        # Lógica de filtrado de queries
│   └── urls.py           # Definición de rutas del módulo
├── models/               # Capa de Datos (Entidades)
│   ├── user.py           # Usuario principal
│   ├── role.py           # Perfiles de acceso
│   └── permission.py     # Acciones atómicas
├── repositories/         # Capa de Persistencia (Queries)
│   ├── user_repo.py
│   ├── role_repo.py
│   └── permission_repo.py
├── services/             # Capa de Negocio (Orquestación)
│   ├── user_service.py
│   ├── role_service.py
│   └── permission_service.py
├── middleware/           # Interceptores de Request
│   └── __init__.py       # (reservado para futuros middlewares)
├── decorators/           # Protecciones de Vista
│   ├── __init__.py       # @require_permission
│   └── README.md
└── utils/                # Utilidades Globales del Módulo
    ├── __init__.py       # Helpers JWT, bcrypt y permisos
    └── README.md
```

## Flujo de Trabajo Recomendado

Para mantener el desacoplamiento, siga este flujo de llamadas:
`API View` → `Service` → `Repository` → `Model`

> [!IMPORTANT]
> **Nunca** importe modelos directamente desde las vistas de API. Utilice siempre la capa de servicios para garantizar que se ejecuten las validaciones de negocio necesarias.

## Guía de Importación

Para mantener un código limpio y evitar dependencias circulares, utilice los puntos de entrada definidos en los archivos `__init__.py`:

### ✅ Prácticas Correctas
```python
# Importar servicios
from apps.accounts.services.user_service import UserService

# Importar modelos (re-exportados en models/__init__.py)
from apps.accounts.models import User, Role

# Usar decoradores
from apps.accounts.decorators import require_permission
```

### ❌ Prácticas a Evitar
```python
# Importar desde archivos internos específicos (rompe el encapsulamiento)
from apps.accounts.models.user import User 

# Consultar la base de datos directamente en el service sin pasar por el repo
User.objects.filter(active=True) 
```

## Responsabilidades de Capas

1.  **Models**: Definen el "qué" (estructura de datos y restricciones de integridad).
2.  **Repositories**: Definen el "cómo buscar" (centralizan las consultas ORM).
3.  **Services**: Definen el "qué hacer" (lógica de negocio, transacciones, validaciones complejas).
4.  **API**: Definen el "cómo exponer" (serialización, códigos de estado, documentación de endpoints).
