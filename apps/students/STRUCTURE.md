# Estructura Técnica: Módulo `students`

Este documento detailing the internal organization and responsibilities of each component within the student management module.

## Árbol de Directorios

```text
students/
├── api/                  # Capa de Entrada (REST)
│   ├── serializers.py    # Esquemas para Estudiantes y Matrículas
│   ├── views.py          # ViewSets estándar
│   └── urls.py           # Registro de rutas vía DefaultRouter
├── models/               # Capa de Datos (Entidades)
│   ├── student.py            # Entidad Estudiante
│   ├── enrollment.py         # Matrícula
│   ├── enrollment_status.py  # Catálogo de estados
│   ├── student_representative.py # Relación estudiante-representante
│   └── representative.py     # Legacy (managed=False)
├── repositories/         # Capa de Persistencia (Queries)
│   └── students_repo.py  # Queries especializadas
├── services/             # Capa de Negocio (Orquestación)
│   └── students_service.py # Lógica de alta y vinculación
└── tests/                # Suites de Pruebas
```

## Modelos Principales

### Student
Información del estudiante vinculada a una Person. El campo `student_code` es único.

### EnrollmentStatus
Catálogo de estados de matrícula (Activo, Retirado, Suspendido, etc.)

### Enrollment
Vinculación de un estudiante a una sección para un año escolar. Incluye campos de sync para operación offline.

### Student_Representative
Vinculación entre estudiante y representante legal. Define parentesco y niveles de autorización.

**Modelo Legacy** (managed=False, no usar):
- `Representative` — Será eliminado tras migración completa

## Flujo de Trabajo Recomendado

Para mantener el desacoplamiento, siga este flujo de llamadas:
`API View` → `Service` → `Repository` → `Model`

> [!IMPORTANT]
> **Nunca** manipule directamente la tabla `Student_Representative` desde las vistas. Utilice siempre `StudentService.assign_representative`.

## Guía de Importación

### ✅ Prácticas Correctas
```python
# Importar servicios
from apps.students.services.students_service import StudentService

# Importar modelos
from apps.students.models import Student, Enrollment, Student_Representative

# Importar repositorios
from apps.students.repositories.students_repo import StudentRepository
```

### ❌ Prácticas a Evitar
```python
from apps.students.models.student import Student
```

## Responsabilidades de Capas

1.  **Models**: Definen la estructura de los datos personales y reglas de parentesco.
2.  **Repositories**: Centralizan la lógica de búsqueda (por código, secciones).
3.  **Services**: Implementan validaciones (edad permitida, unicidad, integridad).
4.  **API**: Exponen los recursos mediante ViewSets con respuestas estandarizadas.