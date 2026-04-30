# Módulo `academic` — Gestión de Infraestructura Académica

Este módulo gestiona la infraestructura académica del sistema, incluyendo configuraciones, períodos, secciones, asignaturas y el sistema de evaluación/calificaciones.

Su diseño sigue una arquitectura desacoplada en capas (Modelos → Repositorios → Servicios → API), garantizando integridad referencial y cálculos centralizados de promedios.

---

## Estructura del Módulo

```
academic/
├── models/         # Entidades de datos
├── repositories/   # Consultas centralizadas (ORM)
├── services/       # Lógica de negocio y cálculos
├── api/            # Serializadores y ViewSets
└── tests/          # Pruebas unitarias y de integración
```

---

## Modelos de Datos

### Config_Academic (Configuración Académica)
Configuración global del año escolar e institución.

| Campo | Tipo | Verbose Name |
| :--- | :--- | :--- |
| `school_year` | ForeignKey (School_Year) | Año Escolar |
| `institution` | ForeignKey (Institution) | Institución |
| `name` | CharField (80) | Nombre |
| `academic_period_type` | CharField (20) | Tipo de Período |
| `number_of_periods` | IntegerField | Cantidad de Períodos |
| `description` | TextField | Descripción |
| `active` | BooleanField | Activo |
| `created_at` | DateTimeField | Fecha de Creación |
| `updated_at` | DateTimeField | Fecha de Actualización |

### Timing_Regime (Régimen de Horario)
Regímenes de asistencia (Matutina, Vespertina, Nocturna).

| Campo | Tipo | Verbose Name |
| :--- | :--- | :--- |
| `school_year` | ForeignKey (School_Year) | Año Escolar |
| `name` | CharField (100) | Nombre del Régimen |
| `description` | TextField | Descripción |
| `active` | BooleanField | Activo |

### Section (Sección)
Representa un grado y paralelo específico.

| Campo | Tipo | Verbose Name |
| :--- | :--- | :--- |
| `school_year` | ForeignKey (School_Year) | Año Escolar |
| `timing_regime` | ForeignKey (Timing_Regime) | Régimen de Horario |
| `level` | CharField (255) | Nivel |
| `grade` | CharField (255) | Grado |
| `parallel` | CharField (255) | Paralelo |
| `capacity` | IntegerField | Capacidad |
| `created_at` | DateTimeField | Fecha de Creación |
| `updated_at` | DateTimeField | Fecha de Actualización |

### Subject (Materia)
Asignaturas vinculadas a una sección.

| Campo | Tipo | Verbose Name |
| :--- | :--- | :--- |
| `school_year` | ForeignKey (School_Year) | Año Escolar |
| `section` | ForeignKey (Section) | Sección |
| `name` | CharField (255) | Nombre de la Materia |
| `code` | CharField (100) | Código |
| `weekly_hours` | IntegerField | Horas Semanales |
| `approve_percentage` | DecimalField | Porcentaje de Aprobación |
| `active` | BooleanField | Activo |
| `created_at` | DateTimeField | Fecha de Creación |
| `updated_at` | DateTimeField | Fecha de Actualización |

---

## Capa de Servicios

### AcademicService (Orquestador principal)

- `create_config_academic`: Crea una nueva configuración académica para un año escolar e institución.
- `update_config_academic`: Actualiza campos específicos de una configuración existente.
- `create_section`: Registra un grado y paralelo validando que no existan duplicados y que la capacidad sea positiva.
- `get_section_details`: Recupera el perfil completo de una sección, incluyendo sus materias, docentes asignados y número de alumnos.
- `create_subject`: Crea una asignatura vinculada a una sección específica del año escolar.
- `list_subjects_by_section`: Retorna la lista ordenada de materias para un grado/paralelo dado.
- `create_academic_activity`: Define una actividad evaluativa (examen, tarea) con su peso y valor máximo permitido.
- `assign_teacher`: Vincula a un docente con una materia y sección, evitando asignaciones duplicadas.
- `record_student_note`: Registra la calificación de un alumno, calculando automáticamente su valor normalizado en base 10.
- `calculate_period_average`: Realiza el cálculo ponderado del promedio de un estudiante en una materia para un período específico.
- `calculate_section_average`: Obtiene el promedio grupal de toda una sección en una asignatura determinada.
- `deactivate_student_note`: Realiza el borrado lógico de una calificación del sistema.

---

## API REST (Resumen)

### Configuración y Regímenes
- GET/POST `/api/academic/config-academic/`
- GET/POST `/api/academic/timing-regime/`

### Secciones y Asignaturas
- GET/POST `/api/academic/section/`
- GET/POST `/api/academic/subject/`
- GET `/api/academic/section/{id}/`
- GET `/api/academic/subject/list_by_section/?section_id={id}`

---

## Seguridad

Header requerido:

```
Authorization: Bearer <token>
```

---

## Pruebas

```
python manage.py test apps.academic
```

---

## Lógica de Calificaciones

1.  **Normalización**: Todas las notas se llevan a escala 10 automáticamente:
    `normalized = (valor / valor_max) * 10`
2.  **Promedios**: Se calculan multiplicando la nota normalizada por el peso de la actividad definido en `Academic_Activity`.
