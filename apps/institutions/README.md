# Módulo `institutions` — Gestión de Base Institucional

Este módulo constituye la base estructural del sistema académico, encargándose de la gestión de la infraestructura escolar básica, incluyendo los años lectivos escolares, los tipos de documento válidos, los niveles académicos educativos y la escala jerárquica de grados estudiantiles.

Su diseño implementa estrictamente una arquitectura en capas desacopladas:

```
Models (Estructura de Datos) ➔ Repositories (Acceso a Datos/Consultas ORM) ➔ Services (Lógica de Negocio) ➔ API (Serializadores, ViewSets y Rutas)
```

---

## Estructura del Módulo

El módulo se organiza físicamente en la siguiente estructura de archivos y directorios:

```
apps/institutions/
├── api/
│   ├── serializers.py      # Transformación y validación de esquemas JSON (School_Year, DocumentType, Grade, Level)
│   ├── urls.py             # Enrutador RESTful para los ViewSets del módulo
│   └── views.py            # ViewSets de DRF con control de acceso basado en HasPermission
├── models/
│   ├── __init__.py         # Punto de entrada y exportación unificada de entidades
│   ├── academic_grade.py   # Grados estudiantiles (5to EGB, 1ero Bachillerato, etc.)
│   ├── academic_level.py   # Niveles de enseñanza (Primaria, Secundaria, Inicial)
│   ├── document_type.py    # Tipos de identificación y cédula (CC, Pasaporte, etc.)
│   ├── school_year.py      # Años lectivos escolares activos e históricos
│   └── section.py          # Aulas físicas y paralelos (consumidas por el módulo academic)
├── repositories/
│   ├── __init__.py         # Exportación unificada de repositorios
│   ├── institution_repo.py # Repositorio de acceso a datos para años escolares
│   └── section_repository.py # Repositorio de acceso a datos para secciones físicas
├── services/
│   ├── __init__.py         # Exportación unificada de servicios
│   └── institution_service.py # Servicio centralizado de lógica de negocio para años lectivos
├── tests/
│   ├── test_api.py         # Pruebas de integración HTTP originales
│   ├── test_api_gaps.py    # Pruebas integrales de brechas de cobertura (RBAC, nuevos ViewSets y modelos)
│   ├── test_models.py      # Pruebas unitarias de modelos de datos
│   └── test_services.py    # Pruebas unitarias de lógica de servicios
├── admin.py                # Configuración de interfaces en Django Admin
├── apps.py                 # Inicialización y configuración de la app django institutions
└── urls.py                 # Enrutador de URL principal de la app
```

---

## Modelos de Datos (Database Schema)

El módulo define e implementa 5 entidades principales en la base de datos. Ninguna consulta directa al ORM de estos modelos se ejecuta en la capa de APIs o de Servicios (salvo en repositorios explícitos).

### 1. School_Year (Año Escolar)

Define el lapso temporal y ciclo escolar lectivo vigente o histórico del sistema.

| Campo        | Tipo Django      | Atributos clave     | Descripción                                           |
| :----------- | :--------------- | :------------------ | :---------------------------------------------------- |
| `id`         | `AutoField`      | Primary Key         | Identificador autoincremental del año escolar.        |
| `name`       | `CharField(255)` | Obligatorio         | Nombre descriptivo del año lectivo (ej. "2024-2025"). |
| `start_date` | `DateField`      | Obligatorio         | Fecha de inicio formal del período lectivo.           |
| `end_date`   | `DateField`      | Obligatorio         | Fecha de finalización formal del período lectivo.     |
| `active`     | `BooleanField`   | `default=True`      | Estado de vigencia y operatividad del año escolar.    |
| `created_at` | `DateTimeField`  | `auto_now_add=True` | Fecha y hora de creación del registro.                |
| `updated_at` | `DateTimeField`  | `auto_now=True`     | Fecha y hora de la última modificación.               |

### 2. DocumentType (Tipo de Documento)

Catálogo unificado de tipos de identificación personal reconocidos por el sistema académico.

| Campo  | Tipo Django      | Atributos clave | Descripción                                                    |
| :----- | :--------------- | :-------------- | :------------------------------------------------------------- |
| `id`   | `AutoField`      | Primary Key     | Identificador del tipo de documento.                           |
| `code` | `CharField(10)`  | `unique=True`   | Código único abreviado del tipo de documento (ej. `CC`, `PP`). |
| `name` | `CharField(100)` | Obligatorio     | Nombre legible completo (ej. "Cédula de Ciudadanía").          |

### 3. AcademicLevel (Nivel Académico)

Representa los grandes niveles educativos generales en los que se segmenta la enseñanza.

| Campo    | Tipo Django      | Atributos clave | Descripción                                            |
| :------- | :--------------- | :-------------- | :----------------------------------------------------- |
| `id`     | `AutoField`      | Primary Key     | Identificador del nivel académico.                     |
| `name`   | `CharField(100)` | Obligatorio     | Nombre legible del nivel educativo (ej. "Secundaria"). |
| `active` | `BooleanField`   | `default=True`  | Estado de vigencia del nivel.                          |

### 4. AcademicGrade (Grado Académico)

Representa cada uno de los peldaños y cursos lectivos específicos dentro de los niveles de enseñanza.

| Campo            | Tipo Django      | Atributos clave            | Descripción                                                                                       |
| :--------------- | :--------------- | :------------------------- | :------------------------------------------------------------------------------------------------ |
| `id`             | `AutoField`      | Primary Key                | Identificador del grado académico.                                                                |
| `academic_level` | `ForeignKey`     | `on_delete=models.CASCADE` | Relación con el nivel general (`institutions.AcademicLevel`).                                     |
| `name`           | `CharField(100)` | Obligatorio                | Nombre descriptivo del grado (ej. "1ero Bachillerato").                                           |
| `subnivel`       | `CharField(20)`  | Choices, nullable, blank   | Subnivel pedagógico: `INICIAL`, `PREPARATORIA`, `ELEMENTAL`, `MEDIA`, `SUPERIOR`, `BACHILLERATO`. |
| `sequence_order` | `IntegerField`   | Obligatorio                | Número secuencial para ordenar cronológicamente los grados.                                       |
| `active`         | `BooleanField`   | `default=True`             | Estado de vigencia del grado académico.                                                           |

### 5. Section (Sección / Aula)

Representa un aula física y paralelo lectivo dentro de un año escolar determinado.

| Campo            | Tipo Django      | Atributos clave                      | Descripción                                                     |
| :--------------- | :--------------- | :----------------------------------- | :-------------------------------------------------------------- |
| `id`             | `AutoField`      | Primary Key                          | Identificador de la sección.                                    |
| `school_year`    | `ForeignKey`     | `on_delete=models.CASCADE`           | Relación con el año lectivo (`institutions.School_Year`).       |
| `academic_grade` | `ForeignKey`     | `on_delete=models.CASCADE`, nullable | Relación con el grado académico (`institutions.AcademicGrade`). |
| `parallel`       | `CharField(255)` | Obligatorio                          | Letra del paralelo asignado (ej. "A", "B").                     |
| `capacity`       | `IntegerField`   | Obligatorio                          | Cupo o capacidad máxima de estudiantes admitidos en el aula.    |
| `active`         | `BooleanField`   | `default=True`                       | Estado de operatividad de la sección física.                    |

---

## Capa de Servicios (Business Logic)

La lógica transaccional de la infraestructura lectiva institucional se administra centralizadamente.

### `InstitutionService`

Orquesta la administración de años escolares y validaciones de rango temporal:

- `create_school_year(name, start_date, end_date)`: Crea e inicializa un nuevo ciclo escolar lectivo. Valida transaccionalmente:
  1.  Que la fecha de inicio sea anterior a la de cierre.
  2.  Que el nuevo rango de fechas no se traslape con ningún año escolar previamente registrado en la base de datos para garantizar coherencia curricular (`ValueError` descriptivo).
- `get_school_year(school_year_id)`: Recupera un año escolar por su PK, lanzando excepción si no es encontrado.
- `list_school_years(active_only=True)`: Lista los años escolares registrados ordenándolos por su fecha de inicio. Permite filtrar solo los activos.
- `get_current_school_year()`: Compara dinámicamente el día de la fecha de hoy contra los rangos escolares lectivos en base de datos para identificar cuál es el año escolar lectivo activo actual. Lanza error si ninguno coincide.
- `update_school_year(school_year_id, **kwargs)`: Modifica parámetros del ciclo escolar validando coherencia de fechas en caso de modificarse.
- `deactivate_school_year(school_year_id)`: Coloca el estado de vigencia del año escolar a `active=False` (borrado lógico).

---

## API Contract (REST API)

Todas las respuestas del módulo implementan de forma estricta la estructura estandarizada `StandardResponseRenderer` en el formato `{"ok": bool, "data": ..., "msg": "..."}`. Las peticiones de listado devuelven un encapsulado de paginación dentro de `data` con la estructura de metadatos (`count`, `next`, `previous`, `results`).

### Rutas Protegidas (JWT Bearer Token requerido)

| Recurso / Acción           | Método HTTP     | Ruta de Endpoint                              | Permiso Requerido                    | Descripción                                                                                            |
| :------------------------- | :-------------- | :-------------------------------------------- | :----------------------------------- | :----------------------------------------------------------------------------------------------------- |
| **Listar Años Escolares**  | `GET`           | `/api/institutions/school-year/`              | `institutions.view_school_year`      | Recupera listado de años escolares activos.                                                            |
| **Crear Año Escolar**      | `POST`          | `/api/institutions/school-year/`              | `institutions.create_school_year`    | Crea e inicializa un nuevo ciclo escolar.                                                              |
| **Detalle Año Escolar**    | `GET`           | `/api/institutions/school-year/{id}/`         | `institutions.view_school_year`      | Obtiene el detalle estructurado de un año escolar.                                                     |
| **Modificar Año Escolar**  | `PUT` / `PATCH` | `/api/institutions/school-year/{id}/`         | `institutions.update_school_year`    | Modifica las propiedades del ciclo lectivo.                                                            |
| **Desactivar Año Escolar** | `DELETE`        | `/api/institutions/school-year/{id}/`         | `institutions.delete_school_year`    | Desactiva lógicamente el año escolar (`active=False`).                                                 |
| **Listar Tipos de Doc.**   | `GET`           | `/api/institutions/document-types/`           | `institutions.view_document_type`    | Recupera catálogo de tipos de documento ( CC, Pasaporte).                                              |
| **Detalle de Tipo Doc.**   | `GET`           | `/api/institutions/document-types/{id}/`      | `institutions.view_document_type`    | Obtiene el detalle de un tipo de documento.                                                            |
| **Listar Secciones**       | `GET`           | `/api/institutions/section/`                  | `institutions.view_section`          | Recupera listado de secciones (aulas y paralelos). Incluye `school_year_name` y `academic_grade_name`. |
| **Crear Sección**          | `POST`          | `/api/institutions/section/`                  | `institutions.create_section`        | Registra una nueva sección física (grado, año, paralelo).                                              |
| **Detalle de Sección**     | `GET`           | `/api/institutions/section/{id}/`             | `institutions.view_section`          | Obtiene el detalle de una sección académica. Incluye `school_year_name` y `academic_grade_name`.       |
| **Modificar Sección**      | `PUT` / `PATCH` | `/api/institutions/section/{id}/`             | `institutions.update_section`        | Modifica propiedades de una sección.                                                                   |
| **Eliminar Sección**       | `DELETE`        | `/api/institutions/section/{id}/`             | `institutions.delete_section`        | Elimina una sección de la base de datos.                                                               |
| **Borrado Lógico Sección** | `POST`          | `/api/institutions/section/{id}/soft-delete/` | `institutions.delete_section`        | Desactiva lógicamente la sección (`active=False`).                                                     |
| **Listar Niveles Acad.**   | `GET`           | `/api/institutions/academic-levels/`          | `institutions.view_academic_level`   | Recupera listado de niveles de enseñanza activos.                                                      |
| **Crear Nivel Académico**  | `POST`          | `/api/institutions/academic-levels/`          | `institutions.create_academic_level` | Inicializa un nuevo nivel de enseñanza.                                                                |
| **Modificar Nivel Acad.**  | `PUT` / `PATCH` | `/api/institutions/academic-levels/{id}/`     | `institutions.update_academic_level` | Modifica metadatos del nivel académico.                                                                |
| **Eliminar Nivel Acad.**   | `DELETE`        | `/api/institutions/academic-levels/{id}/`     | `institutions.delete_academic_level` | Remueve permanentemente el nivel académico.                                                            |
| **Listar Grados Acad.**    | `GET`           | `/api/institutions/academic-grades/`          | `institutions.view_academic_grade`   | Recupera catálogo de grados académicos. Incluye `academic_level_name`.                                 |
| **Crear Grado Académico**  | `POST`          | `/api/institutions/academic-grades/`          | `institutions.create_academic_grade` | Registra un nuevo curso en el sistema.                                                                 |
| **Modificar Grado Acad.**  | `PUT` / `PATCH` | `/api/institutions/academic-grades/{id}/`     | `institutions.update_academic_grade` | Modifica las propiedades del curso.                                                                    |
| **Eliminar Grado Acad.**   | `DELETE`        | `/api/institutions/academic-grades/{id}/`     | `institutions.delete_academic_grade` | Remueve permanentemente el grado del sistema.                                                          |

---

## Formato de Respuestas Enriquecidas

Para proporcionar datos más descriptivos al frontend, los serializers incluyen campos de solo lectura con los nombres relacionados a las ForeignKeys:

### Section (Sección)

Además de los campos `school_year` (ID) y `academic_grade` (ID), la respuesta incluye:

| Campo                 | Tipo     | Descripción                                        |
| :-------------------- | :------- | :------------------------------------------------- |
| `school_year_name`    | `string` | Nombre del año escolar (`school_year.name`)        |
| `academic_grade_name` | `string` | Nombre del grado académico (`academic_grade.name`) |

Ejemplo de respuesta:

```json
{
  "id": 1,
  "school_year": 1,
  "school_year_name": "2024-2025",
  "academic_grade": 3,
  "academic_grade_name": "EGB - 5to Grado",
  "parallel": "A",
  "capacity": 30,
  "active": true
}
```

### AcademicGrade (Grado Académico)

Además del campo `academic_level` (ID), la respuesta incluye:

| Campo                 | Tipo     | Descripción                                        |
| :-------------------- | :------- | :------------------------------------------------- |
| `academic_level_name` | `string` | Nombre del nivel académico (`academic_level.name`) |

Ejemplo de respuesta:

```json
{
  "id": 3,
  "academic_level": 1,
  "academic_level_name": "Educación General Básica",
  "name": "5to Grado",
  "subnivel": "MEDIA",
  "sequence_order": 5,
  "active": true
}
```

---

## Seguridad y Control de Acceso

1.  **Omisión de Permisos**: Los usuarios con la bandera `is_superuser=True` omiten automáticamente cualquier validación de código de permiso.
2.  **Mecanismo de Verificación**: Los ViewSets de DRF aplican `IsAuthenticated` junto a la clase personalizada `HasPermission` de `apps.core.api.permissions`. Dicha clase mapea el nombre de la acción invocada (ej. `list`, `create`, `destroy`) a su respectivo código en la variable declarativa `action_permissions` del ViewSet.
3.  **Bypass de Acceso a Grados y Niveles**: Las vistas de `AcademicLevelViewSet` y `AcademicGradeViewSet` consumen los permisos `institutions.view_academic_level`, `institutions.create_academic_level`, `institutions.update_academic_level`, `institutions.delete_academic_level` y sus equivalentes para `academic_grade`, validando así los accesos administrativos de forma semántica.

---

## Estado de Pruebas y Cobertura (Testing Status)

El módulo posee un conjunto maduro de **26 pruebas unitarias y de integración** distribuidas en la carpeta `tests/`. Todas las pruebas pasan satisfactoriamente bajo el motor SQLite configurado para entornos de pruebas (`--settings=config.settings.test`).

### Escenarios Cubiertos

- **Pruebas de Modelos (`test_models.py`, `test_api_gaps.py`)**: Integridad física del modelo `School_Year`, consistencia en marcas temporales de inicio/fin, representaciones textuales (`__str__`) y creación y consistencia estructural de los modelos `AcademicLevel` y `AcademicGrade`.
- **Pruebas de Lógica de Servicios (`test_services.py`)**: Validación transaccional de detección de traslapes temporales en la creación de años escolares, prevención de fechas de inicio invertidas, consultas del ciclo activo y borrado lógico seguro.
- **Pruebas de Integración y Endpoints de API (`test_api.py`, `test_api_gaps.py`)**: Endpoints de listados, creación y edición de años escolares y tipos de documentos. Validación de naturaleza Read-Only en catálogo de identificaciones.
- **Control de Accesos Basado en Roles y Permisos (RBAC) (`test_api_gaps.py`)**: Pruebas explícitas negativas y positivas que garantizan que usuarios limitados reciban `403 Forbidden` al invocar acciones no asignadas y `200 OK`/`201 Created` al recibir dinámicamente dichos permisos en niveles académicos, grados y ciclos escolares.
