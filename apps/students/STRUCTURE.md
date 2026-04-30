# Estructura Técnica: Módulo `students`

Este documento detalla la organización interna y las responsabilidades de cada componente dentro del módulo de gestión de estudiantes.

## Árbol de Directorios

```text
students/
├── api/                  # Capa de Entrada (REST)
│   ├── serializers.py    # Esquemas para Estudiantes y Representantes
│   ├── views.py          # ViewSets estándar con soporte de acciones
│   └── urls.py           # Registro de rutas vía DefaultRouter
├── models/               # Capa de Datos (Entidades)
│   ├── student.py        # Entidad Estudiante
│   ├── representative.py # Entidad Representante
│   └── student_representative.py # Relación y autorizaciones
├── repositories/         # Capa de Persistencia (Queries)
│   ├── __init__.py       # Exportación de repositorios
│   └── students_repo.py  # Queries especializadas por DNI y sección
├── services/             # Capa de Negocio (Orquestación)
│   └── students_service.py # Lógica de alta y vinculación familiar
└── tests/                # Suites de Pruebas
    └── (test suites)     # Validación de matriculación y relaciones
```

## Flujo de Trabajo Recomendado

Para mantener el desacoplamiento, siga este flujo de llamadas:
`API View` → `Service` → `Repository` → `Model`

> [!IMPORTANT]
> **Nunca** manipule directamente la tabla `Student_Representative` desde las vistas. Utilice siempre `StudentService.assign_representative` para garantizar que se apliquen las reglas de contacto primario y se validen las existencias de ambas entidades.

## Guía de Importación

Utilice los puntos de entrada definidos para evitar dependencias circulares:

### ✅ Prácticas Correctas
```python
# Importar servicios
from apps.students.services.students_service import StudentService

# Importar modelos (re-exportados en models/__init__.py)
from apps.students.models import Student, Representative

# Importar repositorios
from apps.students.repositories.students_repo import StudentRepository
```

### ❌ Prácticas a Evitar
```python
# Importar desde archivos internos específicos
from apps.students.models.student import Student 
```

## Responsabilidades de Capas

1.  **Models**: Definen la estructura de los datos personales y las reglas de parentesco/autorización.
2.  **Repositories**: Centralizan la lógica de búsqueda (por DNI, nombres parciales o secciones).
3.  **Services**: Implementan validaciones de negocio (edad permitida, unicidad, integridad de representantes).
4.  **API**: Exponen los recursos mediante ViewSets que heredan de `BaseStudentViewSet` (o similar) para estandarizar las respuestas.
