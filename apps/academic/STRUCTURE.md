# Estructura Técnica: Módulo `academic`

Este documento detalla la organización interna y las responsabilidades de cada componente dentro del módulo académico.

## Árbol de Directorios

```text
academic/
├── api/                  # Capa de Entrada (REST)
│   ├── serializers.py    # Transformación de datos
│   ├── views.py          # ViewSets con StandardResponse
│   ├── filters.py        # Filtrado avanzado
│   └── urls.py           # Definición de rutas del módulo
├── models/               # Capa de Datos (Entidades)
│   ├── academic_period.py    # Períodos académicos
│   ├── timing_regime.py      # Regímenes de horario
│   ├── section.py            # Secciones (grado/paralelo)
│   ├── subject.py            # Materias
│   ├── subject_academic_config.py # Config de materia por grado
│   ├── subject_offering.py   # Oferta de materia en sección
│   └── teacher_subject_section.py # Asignación docente
├── repositories/         # Capa de Persistencia (Queries)
│   └── academic_repo.py  # Repositorios centralizados por entidad
├── services/             # Capa de Negocio (Orquestación)
│   └── academic_service.py # Lógica de cálculos y validaciones
└── tests/                # Suites de Pruebas
    ├── test_models.py
    ├── test_services.py
    └── test_api.py
```

## Modelos Principales

### Academic_Period
Períodos dentro de un año escolar (Quimestres, parciales, etc.)

### Timing_Regime
Regímenes de asistencia (Matutina, Vespertina, Nocturna).

### Section
Representa un grado y paralelo específico. Vinculada a School_Year, Timing_Regime y AcademicGrade.

### Subject
Asignaturas disponibles en el sistema.

### SubjectAcademicConfig
Vincula una materia a un grado académico con parámetros pedagógicos (horas semanales, orden, etc.)

### SubjectOffering
Instancia de una materia en una sección para un año escolar específico.

### Teacher_Subject_Section
Vinculación entre un docente (User) y una oferta de materia.

**Modelos Legacy** (managed=False, no usar en nuevo código):
- `Config_Academic` — Reemplazado por School_Year → Academic_Period
- `Academic_Activity` — Reemplazado por jerarquía EvaluationMacro → ClassAssignment

## Flujo de Trabajo Recomendado

Para mantener el desacoplamiento, siga este flujo de llamadas:
`API View` → `Service` → `Repository` → `Model`

> [!IMPORTANT]
> **Nunca** realize cálculos de promedios o normalización de notas directamente en los ViewSets. Estas operaciones deben residir exclusivamente en `AcademicService`.

## Guía de Importación

Utilice los puntos de entrada definidos para evitar dependencias circulares y mantener el código limpio:

### ✅ Prácticas Correctas
```python
# Importar servicios
from apps.academic.services.academic_service import AcademicService

# Importar modelos (re-exportados en models/__init__.py)
from apps.academic.models import Section, Subject, SubjectOffering

# Importar repositorios
from apps.academic.repositories.academic_repo import SectionRepository
```

### ❌ Prácticas a Evitar
```python
# Importar desde archivos internos específicos
from apps.academic.models.section import Section

# Realizar cálculos complejos fuera del service
promedio = sum(notas) / len(notas)
```

## Responsabilidades de Capas

1.  **Models**: Definen la estructura y restricciones (ej: `capacity > 0`).
2.  **Repositories**: Centralizan las consultas (ej: `get_active_sections()`).
3.  **Services**: Orquestan la lógica (ej: `record_student_note` valida rangos y normaliza).
4.  **API**: Exponen los recursos mediante ViewSets que heredan de patrones base para estandarizar las respuestas (`ok`, `data`, `msg`).