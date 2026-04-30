# Estructura Técnica: Módulo `institutions`

Este documento detalla la organización interna y las responsabilidades de cada componente dentro del módulo institucional.

## Árbol de Directorios

```text
institutions/
├── api/                  # Capa de Entrada (REST)
│   ├── serializers.py    # Definición de esquemas (3 serializers)
│   ├── views.py          # Controladores (basados en funciones)
│   └── urls.py           # Definición de rutas dinámicas
├── models/               # Capa de Datos (Entidades)
│   ├── institution.py
│   ├── school_year.py
│   └── classroom.py
├── repositories/         # Capa de Persistencia (Queries)
│   └── institution_repo.py # Repositorios centralizados
├── services/             # Capa de Negocio (Orquestación)
│   └── institution_service.py # Lógica de validaciones de fechas
└── tests/                # Suites de Pruebas
    ├── test_models.py
    ├── test_services.py
    └── test_api.py
```

## Flujo de Trabajo Recomendado

Para mantener el desacoplamiento, siga este flujo de llamadas:
`API View` → `Service` → `Repository` → `Model`

> [!IMPORTANT]
> **Nunca** ignore las validaciones de fechas en la creación de años escolares. Utilice siempre `InstitutionService.create_school_year` para evitar solapamientos cronológicos que podrían corromper la lógica de otros módulos (como `academic` o `scheduling`).

## Guía de Importación

Utilice los puntos de entrada definidos para evitar dependencias circulares:

### ✅ Prácticas Correctas
```python
# Importar servicios
from apps.institutions.services.institution_service import InstitutionService

# Importar modelos (re-exportados en models/__init__.py)
from apps.institutions.models import Institution, School_Year

# Importar repositorios
from apps.institutions.repositories.institution_repo import InstitutionRepository
```

### ❌ Prácticas a Evitar
```python
# Importar desde archivos internos específicos (rompe el encapsulamiento)
from apps.institutions.models.institution import Institution 
```

## Responsabilidades de Capas

1.  **Models**: Definen el "qué" (entidades base del sistema).
2.  **Repositories**: Definen el "cómo buscar" (centralizan queries ORM).
3.  **Services**: Definen el "qué hacer" (validaciones complejas de fechas y capacidad).
4.  **API**: Definen el "cómo exponer" (utilizan un sistema de generación de vistas dinámicas para CRUD).
