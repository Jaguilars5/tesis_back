# Módulo `academic` — Gestión de Infraestructura Académica

Este módulo constituye el núcleo de gestión y estructuración de la infraestructura pedagógica y académica del sistema. Se encarga de la administración de materias, períodos académicos, configuraciones curriculares por grado, ofertas de materias en secciones, proyectos interdisciplinarios y la asignación atómica de docentes a sus respectivas materias y cursos.

Su diseño implementa estrictamente una arquitectura en capas desacopladas:

```
Models (Estructura de Datos) ➔ Repositories (Acceso a Datos/Consultas ORM) ➔ Services (Lógica de Negocio) ➔ API (Serializadores, ViewSets y Rutas)
```

---

## Estructura del Módulo

El módulo se organiza físicamente en la siguiente estructura de archivos y directorios:

```
apps/academic/
├── api/
│   ├── filters.py          # Filtros avanzados de búsqueda (Sección, Materia)
│   ├── serializers.py      # Transformación y validación de esquemas JSON (Subject, Section, Period, etc.)
│   ├── urls.py             # Enrutador RESTful para los ViewSets del módulo
│   └── views.py            # ViewSets que heredan de BaseAcademicViewSet con StandardResponse
├── models/
│   ├── __init__.py         # Punto de entrada y exportación unificada de entidades
│   ├── academic_period.py  # Modelo de períodos de evaluación (parciales, trimestres)
│   ├── interdisciplinary_project.py # Modelo de proyectos interdisciplinarios
│   ├── subject.py          # Modelo catálogo de asignaturas disponibles
│   ├── subject_academic_config.py # Configuración curricular de materias por grado
│   ├── subject_offering.py # Oferta concreta de una materia en una sección
│   ├── subject_project.py  # Relación intermedia entre proyectos y ofertas de materia
│   └── teacher_subject_section.py # Asignación de docentes a ofertas de materias
├── repositories/
│   ├── __init__.py         # Exportación unificada de repositorios
│   ├── academic_repo.py    # Repositorios ORM para materias, períodos, ofertas y docentes
│   └── interdisciplinary_project_repository.py # Repositorio ORM para proyectos interdisciplinarios
├── services/
│   ├── __init__.py         # Exportación unificada de servicios
│   └── academic_service.py # Servicio centralizado de lógica de negocio para infraestructura académica
├── tests/
│   ├── test_api.py                # Pruebas de integración HTTP originales
│   ├── test_api_gaps.py           # Pruebas integrales de brechas de cobertura (RBAC, filtros, servicios, nuevos modelos)
│   ├── test_api_permissions.py    # Pruebas exhaustivas de permisos por endpoint
│   ├── test_models.py             # Pruebas unitarias de modelos de datos
│   ├── test_repositories.py       # Pruebas de capa de persistencia
│   └── test_services.py           # Pruebas unitarias sobre lógica de negocio
├── admin.py                # Configuración de interfaces en Django Admin
├── apps.py                 # Inicialización de la aplicación Django academic
├── urls.py                 # Enrutador de URL principal de la app
└── README.md               # Documentación oficial del módulo (Este documento)
```

> [!NOTE]
> La entidad **`Section`** y sus repositorios asociados corresponden físicamente al módulo `institutions` (Capa de Infraestructura Institucional), pero se exponen y consumen en los flujos académicos del ViewSet en este módulo para consolidar la experiencia del usuario.

---

## Modelos de Datos (Database Schema)

El módulo define e implementa 7 entidades principales en la base de datos. Ninguna consulta directa al ORM de estos modelos se ejecuta en la capa de APIs; todas son encapsuladas en sus respectivos Repositories.

### 1. Subject (Materia)

Representa las asignaturas que forman parte del catálogo general del sistema.

| Campo        | Tipo Django      | Atributos clave     | Descripción                                                  |
| :----------- | :--------------- | :------------------ | :----------------------------------------------------------- |
| `id`         | `AutoField`      | Primary Key         | Identificador autoincremental de la materia.                 |
| `name`       | `CharField(255)` | Obligatorio         | Nombre descriptivo de la materia (ej. "Matemáticas").        |
| `code`       | `CharField(100)` | `unique=True`       | Código único de identificación de la materia (ej. `MAT101`). |
| `is_active`  | `BooleanField`   | `default=True`      | Estado de vigencia de la materia.                            |
| `created_at` | `DateTimeField`  | `auto_now_add=True` | Fecha y hora de creación de la materia.                      |
| `updated_at` | `DateTimeField`  | `auto_now=True`     | Fecha y hora de la última actualización.                     |

### 2. AcademicPeriod (Período Académico)

Representa los lapsos de tiempo de evaluación que estructuran un año lectivo escolar.

| Campo               | Tipo Django     | Atributos clave              | Descripción                                                    |
| :------------------ | :-------------- | :--------------------------- | :------------------------------------------------------------- |
| `id`                | `AutoField`     | Primary Key                  | Identificador del período académico.                           |
| `school_year`       | `ForeignKey`    | `on_delete=models.CASCADE`   | Relación con el año lectivo (`institutions.SchoolYear`).      |
| `name`              | `CharField(80)` | Obligatorio                  | Nombre legible del período (ej. "Primer Trimestre").           |
| `period_type`       | `ForeignKey`    | `on_delete=models.SET_NULL`, nullable | Relación con el tipo de período (`academic.PeriodType`). |
| `start_date`        | `DateField`     | Obligatorio                  | Fecha de inicio formal del período académico.                  |
| `end_date`          | `DateField`     | Obligatorio                  | Fecha de finalización formal del período académico.            |
| `is_regular_period` | `BooleanField`  | `default=True`               | Indica si el período es de cursada estándar o de recuperación. |

### 3. SubjectAcademicConfig (Configuración Curricular por Grado)

Establece los parámetros y horas semanales asignadas a una asignatura dentro de un grado lectivo específico.

| Campo               | Tipo Django    | Atributos clave            | Descripción                                                     |
| :------------------ | :------------- | :------------------------- | :-------------------------------------------------------------- |
| `id`                | `AutoField`    | Primary Key                | Identificador de la configuración curricular.                   |
| `subject`           | `ForeignKey`   | `on_delete=models.CASCADE` | Relación con la asignatura base (`academic.Subject`).           |
| `academic_grade`    | `ForeignKey`   | `on_delete=models.CASCADE` | Relación con el grado académico (`institutions.AcademicGrade`). |
| `weekly_hours`      | `IntegerField` | Obligatorio                | Cantidad de horas lectivas dictadas a la semana.                |
| `pedagogical_order` | `IntegerField` | Obligatorio                | Orden de precedencia o peso pedagógico.                         |
| `is_required`       | `BooleanField` | `default=True`             | Define si la materia es de carácter obligatorio u optativo.     |
| `is_active`         | `BooleanField` | `default=True`             | Estado de vigencia de la configuración.                         |

### 4. SubjectOffering (Oferta de Materia)

Instancia curricular concreta que asocia un grado académico y paralelo (Sección) con una asignatura para un año lectivo.

| Campo                     | Tipo Django    | Atributos clave            | Descripción                                               |
| :------------------------ | :------------- | :------------------------- | :-------------------------------------------------------- |
| `id`                      | `AutoField`    | Primary Key                | Identificador de la oferta.                               |
| `school_year`             | `ForeignKey`   | `on_delete=models.CASCADE` | Relación con el año lectivo (`institutions.SchoolYear`). |
| `section`                 | `ForeignKey`   | `on_delete=models.CASCADE` | Relación con la sección física (`institutions.Section`).  |
| `subject_academic_config` | `ForeignKey`   | `on_delete=models.CASCADE` | Relación con la configuración curricular base.            |
| `is_active`               | `BooleanField` | `default=True`             | Determina si la oferta se encuentra activa.               |

- **Constraint**: Restricción `unique_together = ("school_year", "section", "subject_academic_config")` que previene duplicación de ofertas curriculares en una misma aula.

### 5. TeacherSubjectSection (Asignación Docente)

Vínculo contractual que define qué usuario (docente) dicta una oferta de materia activa en un aula.

| Campo              | Tipo Django     | Atributos clave            | Descripción                                                     |
| :----------------- | :-------------- | :------------------------- | :-------------------------------------------------------------- |
| `id`               | `AutoField`     | Primary Key                | Identificador de la asignación.                                 |
| `user`             | `ForeignKey`    | `on_delete=models.CASCADE` | Relación con la cuenta del docente (`iam.User`).           |
| `subject_offering` | `ForeignKey`    | `on_delete=models.CASCADE` | Relación con la oferta curricular (`academic.SubjectOffering`). |
| `is_active`        | `BooleanField`  | `default=True`             | Estado de vigencia del vínculo.                                 |
| `created_at`       | `DateTimeField` | `auto_now_add=True`        | Fecha y hora de creación de la asignación.                      |
| `updated_at`       | `DateTimeField` | `auto_now=True`            | Fecha y hora de la última actualización.                        |

### 6. InterdisciplinaryProject (Proyecto Interdisciplinario)

Representa proyectos académicos integrados que abarcan múltiples asignaturas dentro de un período académico.

| Campo             | Tipo Django      | Atributos clave            | Descripción                                                          |
| :---------------- | :--------------- | :------------------------- | :------------------------------------------------------------------- |
| `id`              | `AutoField`      | Primary Key                | Identificador del proyecto.                                          |
| `academic_period` | `ForeignKey`     | `on_delete=models.CASCADE` | Relación con el período académico base (`academic.AcademicPeriod`). |
| `title`           | `CharField(200)` | Obligatorio                | Título del proyecto interdisciplinario.                              |
| `description`     | `TextField`      | Nullable, Blank            | Detalle de objetivos y alcance del proyecto.                         |
| `start_date`      | `DateField`      | Obligatorio                | Fecha de inicio del proyecto.                                        |
| `delivery_date`   | `DateField`      | Obligatorio                | Fecha límite de entrega de resultados.                               |
| `is_active`       | `BooleanField`   | `default=True`             | Estado de vigencia del proyecto.                                     |

### 7. SubjectProject (Asignaturas Vinculadas al Proyecto)

Modelo intermedio explícito que asocia las materias particulares que participan en el desarrollo del proyecto interdisciplinario.

| Campo                       | Tipo Django  | Atributos clave            | Descripción                                        |
| :-------------------------- | :----------- | :------------------------- | :------------------------------------------------- |
| `id`                        | `AutoField`  | Primary Key                | Identificador del vínculo.                         |
| `interdisciplinary_project` | `ForeignKey` | `on_delete=models.CASCADE` | Relación con el proyecto interdisciplinario.       |
| `subject_offering`          | `ForeignKey` | `on_delete=models.CASCADE` | Relación con la oferta de asignatura participante. |

- **Constraint**: Restricción `unique_together = ("interdisciplinary_project", "subject_offering")` que impide vincular por duplicado una misma asignatura a un proyecto.

---

## Capa de Servicios (Business Logic)

La lógica de negocio se procesa de forma integrada en la clase de servicios. Los métodos están adaptados para asegurar coherencia y evitar desalineaciones con las propiedades físicas de los modelos.

### `AcademicService`

Administra el ciclo de vida y la coherencia de la infraestructura académica escolar:

- `create_section(school_year_id, academic_grade_id, parallel, capacity)`: Registra una nueva sección física previa validación de que la capacidad del aula sea mayor a cero.
- `get_section(section_id)`: Recupera la sección de BD y lanza una excepción descriptiva en caso de que no exista.
- `get_section_details(section_id)`: Orquesta una consulta combinada para retornar los datos básicos del aula, su cantidad actual de estudiantes matriculados, asignaciones docentes y ofertas de materias activas.
- `update_section(section_id, **kwargs)`: Aplica modificaciones a las propiedades de la sección previa validación.
- `create_subject(name, code)`: Crea y cataloga una nueva materia en el sistema.
- `get_subject_details(subject_id)`: Recupera el detalle de una asignatura indicando sus configuraciones por grado y docentes asociados.
- `create_academic_period(name, school_year_id, period_type="REGULAR", start_date=None, end_date=None, is_regular_period=True)`: Crea e inicializa un período académico con sus fechas formales y tipología. Valida la obligatoriedad de marcas temporales de inicio/fin.
- `assign_teacher(user_id, subject_offering_id)`: Vincula de forma atómica a un docente con una oferta curricular. Lanza `ValueError` en caso de detectar una asignación duplicada activa.
- `list_teacher_assignments(user_id=None, subject_offering_id=None)`: Filtra y lista de forma flexible las asignaciones docentes del sistema.
- `remove_teacher_assignment(assignment_id)`: Remueve de manera permanente una asignación docente.

---

## API Contract (REST API)

Todas las respuestas del módulo implementan de forma estricta la estructura estandarizada `StandardResponseRenderer` en el formato `{"ok": bool, "data": ..., "msg": "..."}`. Las peticiones de listado devuelven un encapsulado de paginación dentro de `data` con la estructura de metadatos (`count`, `next`, `previous`, `results`).

### Rutas Protegidas (JWT Bearer Token requerido)

| Recurso / Acción              | Método HTTP     | Ruta de Endpoint                                          | Permiso Requerido                 | Descripción                                                        |
| :---------------------------- | :-------------- | :-------------------------------------------------------- | :-------------------------------- | :----------------------------------------------------------------- |
| **Listar Materias**           | `GET`           | `/api/academic/subject/`                                  | `academic.view_subject`           | Recupera el catálogo de materias configuradas.                     |
| **Crear Materia**             | `POST`          | `/api/academic/subject/`                                  | `academic.create_subject`         | Cataloga una nueva asignatura.                                     |
| **Actualizar Materia**        | `PUT` / `PATCH` | `/api/academic/subject/{id}/`                             | `academic.update_subject`         | Modifica metadatos de la asignatura.                               |
| **Eliminar Materia**          | `DELETE`        | `/api/academic/subject/{id}/`                             | `academic.delete_subject`         | Elimina la materia del sistema académico.                          |
| **Borrado Lógico Materia**    | `POST`          | `/api/academic/subject/{id}/soft-delete/`                 | `academic.delete_subject`         | Coloca el estado de vigencia a `active=False`.                     |
| **Listar Períodos**           | `GET`           | `/api/academic/academic-period/`                          | `academic.view_period`            | Recupera el catálogo de parciales y trimestres.                    |
| **Crear Período**             | `POST`          | `/api/academic/academic-period/`                          | `academic.create_period`          | Crea e inicializa un nuevo lapso evaluativo.                       |
| **Listar Asignaciones**       | `GET`           | `/api/academic/teacher-subject-section/`                  | `academic.view_teacher_subject`   | Lista asignaciones de docentes a cursos.                           |
| **Vincular Docente**          | `POST`          | `/api/academic/teacher-subject-section/`                  | `academic.create_teacher_subject` | Genera la asignación docente-materia-sección.                      |
| **Borrado Lógico Asignación** | `POST`          | `/api/academic/teacher-subject-section/{id}/soft-delete/` | `academic.delete_teacher_subject` | Desactiva lógicamente el vínculo docente (`active=False`).         |
| **Listar Config. Curricular** | `GET`           | `/api/academic/subject-academic-configs/`                 | `academic.view_subject`           | Lista horas semanales y exigencias de materias por grado.          |
| **Crear Config. Curricular**  | `POST`          | `/api/academic/subject-academic-configs/`                 | `academic.create_subject`         | Define parámetros de asignatura para un grado.                     |
| **Listar Ofertas Materia**    | `GET`           | `/api/academic/subject-offerings/`                        | `academic.view_subject`           | Lista ofertas curriculares de materias en aulas.                   |
| **Crear Oferta Materia**      | `POST`          | `/api/academic/subject-offerings/`                        | `academic.create_subject`         | Habilita una asignatura en un aula para el año escolar.            |
| **Listar Proyectos Inter.**   | `GET`           | `/api/academic/interdisciplinary-projects/`               | `academic.view_config`            | Lista proyectos interdisciplinarios evaluativos.                   |
| **Crear Proyecto Inter.**     | `POST`          | `/api/academic/interdisciplinary-projects/`               | `academic.create_config`          | Inicializa un proyecto interdisciplinario en un parcial/trimestre. |
| **Listar Materias de Proy.**  | `GET`           | `/api/academic/subject-projects/`                         | `academic.view_config`            | Lista relaciones de asignaturas anexadas a proyectos.              |
| **Asociar Materia a Proy.**   | `POST`          | `/api/academic/subject-projects/`                         | `academic.create_config`          | Vincula una oferta de asignatura al desarrollo de un proyecto.     |

---

## Formato de Respuestas Enriquecidas

Los serializers del módulo incluyen campos de solo lectura con los nombres relacionados a las ForeignKeys, para proporcionar datos más descriptivos al frontend.

### AcademicPeriod (Período Académico)

Además del campo `school_year` (ID), la respuesta incluye:

| Campo              | Tipo     | Descripción                                 |
| :----------------- | :------- | :------------------------------------------ |
| `school_year_name` | `string` | Nombre del año escolar (`school_year.name`) |

```json
{
  "id": 1,
  "school_year": 1,
  "school_year_name": "2024-2025",
  "name": "Primer Trimestre",
  "period_type": "REGULAR",
  "start_date": "2024-09-01",
  "end_date": "2024-12-20"
}
```

### TeacherSubjectSection (Asignación Docente)

Además de los campos `user` (ID) y `subject_offering` (ID), la respuesta incluye:

| Campo                   | Tipo     | Descripción                                                      |
| :---------------------- | :------- | :--------------------------------------------------------------- |
| `user_name`             | `string` | Nombre completo del docente (`user.person.get_full_name()`)      |
| `subject_offering_name` | `string` | Representación textual de la oferta (`subject_offering.__str__`) |

### SubjectAcademicConfig (Configuración Curricular)

Además de los campos `subject` (ID) y `academic_grade` (ID), la respuesta incluye:

| Campo                 | Tipo     | Descripción                                        |
| :-------------------- | :------- | :------------------------------------------------- |
| `subject_name`        | `string` | Nombre de la materia (`subject.name`)              |
| `academic_grade_name` | `string` | Nombre del grado académico (`academic_grade.name`) |

### SubjectOffering (Oferta de Materia)

Además de los campos `school_year`, `section` y `subject_academic_config` (IDs), la respuesta incluye:

| Campo                          | Tipo     | Descripción                                                                    |
| :----------------------------- | :------- | :----------------------------------------------------------------------------- |
| `school_year_name`             | `string` | Nombre del año escolar (`school_year.name`)                                    |
| `section_name`                 | `string` | Representación textual de la sección (`section.__str__`)                       |
| `subject_academic_config_name` | `string` | Representación textual de la configuración (`subject_academic_config.__str__`) |

### SubjectProject (Asignatura de Proyecto)

Además de los campos `interdisciplinary_project` (ID) y `subject_offering` (ID), la respuesta incluye:

| Campo                             | Tipo     | Descripción                                                                |
| :-------------------------------- | :------- | :------------------------------------------------------------------------- |
| `interdisciplinary_project_title` | `string` | Título del proyecto interdisciplinario (`interdisciplinary_project.title`) |
| `subject_offering_name`           | `string` | Representación textual de la oferta (`subject_offering.__str__`)           |

### InterdisciplinaryProject (Proyecto Interdisciplinario)

Además del campo `academic_period` (ID), la respuesta incluye:

| Campo                  | Tipo     | Descripción                                           |
| :--------------------- | :------- | :---------------------------------------------------- |
| `academic_period_name` | `string` | Nombre del período académico (`academic_period.name`) |

---

## Estado de Pruebas y Cobertura (Testing Status)

El módulo posee **102 pruebas unitarias y de integración** distribuidas en **6 archivos** dentro de `tests/`. Todas las pruebas pasan satisfactoriamente bajo el motor SQLite configurado para entornos de pruebas (`--settings=config.settings.test`).

### Escenarios Cubiertos

- **Pruebas de Modelos (`test_models.py`, `test_api_gaps.py`)**: Creación y validación de restricciones en base de datos de todos los modelos curriculares (`AcademicPeriod`, `SubjectOffering`, `SubjectAcademicConfig`, `TeacherSubjectSection`, `InterdisciplinaryProject`, `SubjectProject`), integridad referencial y representaciones textuales.
- **Pruebas de Lógica de Servicios (`test_services.py`, `test_api_gaps.py`)**: Cobertura atómica de métodos del `AcademicService` (`create_section`, `create_subject`, `create_academic_period`, `assign_teacher` y detección de asignaciones docentes por duplicado).
- **Pruebas de Integración de APIs (`test_api.py`, `test_api_gaps.py`)**: Listado, creación, detalle y actualización de secciones, materias, períodos académicos, asignaciones de docentes, ofertas curriculares y proyectos.
- **Control de Accesos Basado en Roles y Permisos (RBAC) (`test_api_gaps.py`)**: Validación negativa que garantiza que usuarios no autorizados reciban un código de estado `403 Forbidden` al listar o crear registros del módulo, y validación positiva que otorga accesos `200 OK`/`201 Created` al recibir dinámicamente el permiso.

---

## Modelos de Catálogo
- **PeriodType** — Tipo de período académico (REGULAR, SUPLETORIO, REFUERZO)
