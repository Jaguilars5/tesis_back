# Módulo `institutions` — Gestión de Base Institucional

Este módulo constituye la base estructural del sistema académico, encargándose de la gestión de la infraestructura escolar, incluyendo años lectivos, niveles académicos, sublevels, grados y secciones (aulas/paralelos). También expone el catálogo de tipos de documento (modelo alojado en `people`).

Su diseño implementa estrictamente una arquitectura en capas desacopladas:

```
Models (Estructura de Datos) ➔ Repositories (Acceso a Datos/Consultas ORM) ➔ Services (Lógica de Negocio) ➔ API (Serializadores, ViewSets y Rutas)
```

---

## Estructura del Módulo

```
apps/institutions/
├── api/
│   ├── serializers.py      # Transformación y validación de esquemas JSON (SchoolYear, Section, AcademicLevel, AcademicSublevel, AcademicGrade)
│   ├── urls.py             # Enrutador RESTful via DefaultRouter (5 ViewSets)
│   └── views.py            # ViewSets de DRF con control de acceso basado en HasPermission
├── models/
│   ├── __init__.py         # Punto de entrada y exportación unificada de entidades
│   ├── school_year.py      # Años lectivos escolares activos e históricos
│   ├── academic_level.py   # Niveles de enseñanza (Primaria, Secundaria, Inicial)
│   ├── academic_sublevel.py# Sublevels pedagógicos vinculados a AcademicLevel
│   ├── academic_grade.py   # Grados estudiantiles (5to EGB, 1ero Bachillerato, etc.)
│   └── section.py          # Aulas físicas y paralelos
├── repositories/
│   ├── __init__.py         # Exportación unificada de repositorios
│   ├── institution_repo.py # Repositorio para SchoolYear, hereda de BaseRepository
│   └── section_repository.py # Repositorio para Section con queries específicas (por año, grado)
├── services/
│   ├── __init__.py
│   └── institution_service.py # Lógica de negocio para años lectivos (creación, solapamiento, ciclo actual)
├── tests/
│   ├── test_models.py          # Pruebas unitarias de modelos
│   ├── test_repositories.py    # Pruebas de capa de persistencia (SchoolYearRepository, SectionRepository)
│   ├── test_services.py        # Pruebas de lógica de servicios
│   ├── test_api.py             # Pruebas de integración HTTP
│   ├── test_api_gaps.py        # Pruebas de brechas: modelos adicionales y RBAC
│   └── test_api_permissions.py # Pruebas exhaustivas de permisos por endpoint
├── admin.py                # Configuración de interfaces en Django Admin
├── apps.py                 # Inicialización y configuración de la app django institutions
├── STRUCTURE.md            # Documentación técnica detallada de estructura interna
└── urls.py                 # Enrutador de URL principal de la app
```

---

## Modelos de Datos (Database Schema)

El módulo define **5 entidades propias** en la base de datos. Ninguna consulta directa al ORM se ejecuta en la capa de APIs o Servicios (salvo en repositorios explícitos).

### 1. SchoolYear (Año Escolar)

Define el lapso temporal y ciclo escolar lectivo vigente o histórico del sistema.

| Campo        | Tipo Django      | Atributos clave     | Descripción                                           |
| :----------- | :--------------- | :------------------ | :---------------------------------------------------- |
| `id`         | `AutoField`      | Primary Key         | Identificador autoincremental del año escolar.        |
| `name`       | `CharField(255)` | Obligatorio         | Nombre descriptivo del año lectivo (ej. "2024-2025"). |
| `start_date` | `DateField`      | Obligatorio         | Fecha de inicio formal del período lectivo.           |
| `end_date`   | `DateField`      | Obligatorio         | Fecha de finalización formal del período lectivo.     |
| `is_active`  | `BooleanField`   | `default=True`      | Estado de vigencia y operatividad del año escolar.    |

### 2. AcademicLevel (Nivel Académico)

Representa los grandes niveles educativos generales en los que se segmenta la enseñanza.

| Campo       | Tipo Django      | Atributos clave | Descripción                                            |
| :---------- | :--------------- | :-------------- | :----------------------------------------------------- |
| `id`        | `AutoField`      | Primary Key     | Identificador del nivel académico.                     |
| `name`      | `CharField(100)` | Obligatorio     | Nombre legible del nivel educativo (ej. "Secundaria"). |
| `code`      | `CharField(50)` | `blank=True, db_index=True` | Código único del nivel (ej. `SEC`, `BAS`, `BACH`).    |
| `is_active` | `BooleanField`   | `default=True`  | Estado de vigencia del nivel.                          |

### 3. AcademicSublevel (Sublevel Académico)

Representa la subdivisión pedagógica dentro de un nivel académico. Reemplaza al antiguo campo `sublevel` con choices del modelo `AcademicGrade`. Expuesto via API en `/api/institutions/academic-sublevel/`.

| Campo            | Tipo Django      | Atributos clave            | Descripción                                                  |
| :--------------- | :--------------- | :------------------------- | :----------------------------------------------------------- |
| `id`             | `AutoField`      | Primary Key                | Identificador del sublevel.                                  |
| `academic_level` | `ForeignKey`     | `on_delete=models.CASCADE` | Relación con el nivel general (`institutions.AcademicLevel`).|
| `code`           | `CharField(20)`  | `unique=True`              | Código único del sublevel (ej. `BASICA`, `BACHILLERATO`).    |
| `name`           | `CharField(100)` | Obligatorio                | Nombre legible del sublevel (ej. "Básica", "Bachillerato").  |
| `description`    | `TextField`      | `blank=True`               | Descripción opcional del sublevel.                           |
| `is_active`      | `BooleanField`   | `default=True`             | Estado de vigencia del sublevel.                             |

### 4. AcademicGrade (Grado Académico)

Representa cada uno de los peldaños y cursos lectivos específicos dentro de los sublevels de enseñanza.

| Campo              | Tipo Django        | Atributos clave               | Descripción                                                              |
| :----------------- | :----------------- | :---------------------------- | :----------------------------------------------------------------------- |
| `id`               | `AutoField`        | Primary Key                   | Identificador del grado académico.                                       |
| `academic_sublevel`| `ForeignKey`       | `on_delete=models.PROTECT`    | Relación con el sublevel (`institutions.AcademicSublevel`).              |
| `code`             | `CharField(50)`   | `blank=True, db_index=True`                | Código único del grado (ej. `5TO_EGB`, `1ERO_BACH`).                    |
| `name`             | `CharField(100)`   | Obligatorio                   | Nombre descriptivo del grado (ej. "1ero Bachillerato").                  |
| `sequence_order`   | `IntegerField`     | Obligatorio                   | Número secuencial para ordenar cronológicamente los grados.              |
| `is_active`        | `BooleanField`     | `default=True`                | Estado de vigencia del grado académico.                                  |

> **Nota**: `AcademicGrade` expone la propiedad `academic_level` que resuelve el nivel desde `academic_sublevel.academic_level`. El serializer incluye `academic_level_name` como campo de solo lectura.

### 5. Section (Sección / Aula)

Representa un aula física y paralelo lectivo dentro de un año escolar determinado.

| Campo            | Tipo Django      | Atributos clave                      | Descripción                                                     |
| :--------------- | :--------------- | :----------------------------------- | :-------------------------------------------------------------- |
| `id`             | `AutoField`      | Primary Key                          | Identificador de la sección.                                    |
| `school_year`    | `ForeignKey`     | `on_delete=models.CASCADE`           | Relación con el año lectivo (`institutions.SchoolYear`).        |
| `academic_grade` | `ForeignKey`     | `on_delete=models.CASCADE`, nullable | Relación con el grado académico (`institutions.AcademicGrade`). |
| `code`           | `CharField(50)`  | `blank=True, db_index=True`| Código único de la sección (ej. `2024-8A`, `2025-1B`).         |
| `parallel`       | `CharField(255)` | Obligatorio                          | Letra del paralelo asignado (ej. "A", "B").                     |
| `capacity`       | `IntegerField`   | Obligatorio                          | Cupo o capacidad máxima de estudiantes admitidos en el aula.    |
| `is_active`      | `BooleanField`   | `default=True`                       | Estado de operatividad de la sección física.                    |

---

## Capa de Servicios (Business Logic)

### `InstitutionService`

Orquesta la administración de años escolares y validaciones de rango temporal:

- `create_school_year(name, start_date, end_date)`: Crea e inicializa un nuevo ciclo escolar. Valida transaccionalmente que la fecha de inicio sea anterior a la de cierre y que el rango no se traslape con años existentes (`ValueError`).
- `get_school_year(school_year_id)`: Recupera un año escolar por PK. Lanza `ValueError` si no existe.
- `list_school_years(active_only=True)`: Lista años escolares ordenados por `-start_date`. Filtra solo activos por defecto.
- `get_current_school_year()`: Determina el año escolar activo cuya ventana de fechas contiene la fecha actual. Lanza `ValueError` si ninguno coincide.
- `update_school_year(school_year_id, **kwargs)`: Modifica parámetros validando coherencia de fechas.
- `deactivate_school_year(school_year_id)`: Borrado lógico (`is_active=False`).

---

## API Contract (REST API)

Todas las respuestas implementan `StandardResponseRenderer` con formato `{"ok": bool, "data": ..., "msg": "..."}`. Los listados de entidades con ViewSet paginado devuelven `data` con `{ count, next, previous, results }`.

### Rutas Protegidas (JWT Bearer Token requerido)

| Recurso / Acción             | Método HTTP     | Ruta de Endpoint                                | Permiso Requerido                        | Descripción                                                                                       |
| :--------------------------- | :-------------- | :---------------------------------------------- | :--------------------------------------- | :------------------------------------------------------------------------------------------------ |
| **Listar Años Escolares**    | `GET`           | `/api/institutions/school-year/`                | `institutions.view_school_year`          | Lista años escolares (activos por defecto).                                                       |
| **Crear Año Escolar**        | `POST`          | `/api/institutions/school-year/`                | `institutions.create_school_year`        | Crea un nuevo ciclo escolar con validación de solapamiento.                                       |
| **Detalle Año Escolar**      | `GET`           | `/api/institutions/school-year/{id}/`           | `institutions.view_school_year`          | Obtiene detalle de un año escolar.                                                                |
| **Modificar Año Escolar**    | `PUT` / `PATCH` | `/api/institutions/school-year/{id}/`           | `institutions.update_school_year`        | Modifica propiedades del ciclo lectivo.                                                           |
| **Desactivar Año Escolar**   | `DELETE`        | `/api/institutions/school-year/{id}/`           | `institutions.delete_school_year`        | Borrado lógico (`is_active=False`) vía `InstitutionService.deactivate_school_year`.               |
| **Listar Secciones**         | `GET`           | `/api/institutions/section/`                    | `institutions.view_section`              | Lista secciones ordenadas por grado y paralelo. Incluye `school_year_name` y `academic_grade_name`.|
| **Crear Sección**            | `POST`          | `/api/institutions/section/`                    | `institutions.create_section`            | Registra una nueva sección (aula/paralelo).                                                       |
| **Detalle de Sección**       | `GET`           | `/api/institutions/section/{id}/`               | `institutions.view_section`              | Obtiene detalle de una sección.                                                                   |
| **Modificar Sección**        | `PUT` / `PATCH` | `/api/institutions/section/{id}/`               | `institutions.update_section`            | Modifica propiedades de una sección.                                                              |
| **Eliminar Sección**         | `DELETE`        | `/api/institutions/section/{id}/`               | `institutions.delete_section`            | Eliminación física de la sección.                                                                 |
| **Borrado Lógico Sección**   | `POST`          | `/api/institutions/section/{id}/soft-delete/`   | `institutions.delete_section`            | Desactiva lógicamente la sección (`is_active=False`).                                             |
| **Listar Niveles Acad.**     | `GET`           | `/api/institutions/academic-levels/`            | `institutions.view_academic_level`       | Lista niveles de enseñanza.                                                                       |
| **Crear Nivel Académico**    | `POST`          | `/api/institutions/academic-levels/`            | `institutions.create_academic_level`     | Crea un nuevo nivel de enseñanza.                                                                 |
| **Modificar Nivel Acad.**    | `PUT` / `PATCH` | `/api/institutions/academic-levels/{id}/`       | `institutions.update_academic_level`     | Modifica metadatos del nivel.                                                                     |
| **Eliminar Nivel Acad.**     | `DELETE`        | `/api/institutions/academic-levels/{id}/`       | `institutions.delete_academic_level`     | Eliminación física del nivel.                                                                     |
| **Listar Sublevels Acad.**  | `GET`           | `/api/institutions/academic-sublevel/`           | `institutions.view_academic_sublevel`    | Lista sublevels académicos ordenados por `name`. Incluye `academic_level_name`.          |
| **Crear Sublevel Académico** | `POST`          | `/api/institutions/academic-sublevel/`           | `institutions.create_academic_sublevel`  | Registra un nuevo sublevel. Requiere `academic_level` (FK).                                       |
| **Detalle Sublevel Acad.**   | `GET`           | `/api/institutions/academic-sublevel/{id}/`      | `institutions.view_academic_sublevel`    | Obtiene detalle de un sublevel.                                                                    |
| **Modificar Sublevel Acad.** | `PUT` / `PATCH` | `/api/institutions/academic-sublevel/{id}/`      | `institutions.update_academic_sublevel`  | Modifica propiedades del sublevel.                                                                 |
| **Eliminar Sublevel Acad.**  | `DELETE`        | `/api/institutions/academic-sublevel/{id}/`      | `institutions.delete_academic_sublevel`  | Eliminación física del sublevel.                                                                   |
| **Listar Grados Acad.**      | `GET`           | `/api/institutions/academic-grades/`            | `institutions.view_academic_grade`       | Lista grados académicos ordenados por `sequence_order`. Incluye `academic_level_name`.             |
| **Crear Grado Académico**    | `POST`          | `/api/institutions/academic-grades/`            | `institutions.create_academic_grade`     | Registra un nuevo grado. Requiere `academic_sublevel` (FK).                                       |
| **Modificar Grado Acad.**    | `PUT` / `PATCH` | `/api/institutions/academic-grades/{id}/`       | `institutions.update_academic_grade`     | Modifica propiedades del grado.                                                                   |
| **Eliminar Grado Acad.**     | `DELETE`        | `/api/institutions/academic-grades/{id}/`       | `institutions.delete_academic_grade`     | Eliminación física del grado.                                                                     |



---

## Formato de Respuestas Enriquecidas

Los serializers incluyen campos de solo lectura con nombres relacionados a ForeignKeys:

### Section (Sección)

Además de `school_year` (ID) y `academic_grade` (ID), la respuesta incluye:

| Campo                 | Tipo     | Descripción                                        |
| :-------------------- | :------- | :------------------------------------------------- |
| `school_year_name`    | `string` | Nombre del año escolar (`school_year.name`)        |
| `academic_grade_name` | `string` | Nombre del grado académico (`academic_grade.name`) |

```json
{
  "id": 1,
  "school_year": 1,
  "school_year_name": "2024-2025",
  "academic_grade": 3,
  "academic_grade_name": "EGB - 5to Grado",
  "parallel": "A",
  "capacity": 30,
  "is_active": true
}
```

### AcademicSublevel (Sublevel Académico)

Además de `academic_level` (ID), la respuesta incluye `academic_level_name` (resuelto vía FK):

| Campo                 | Tipo     | Descripción                                              |
| :-------------------- | :------- | :------------------------------------------------------- |
| `academic_level_name` | `string` | Nombre del nivel académico (`academic_level.name`)       |

```json
{
  "id": 1,
  "academic_level": 1,
  "academic_level_name": "Educación General Básica",
  "code": "BASICA",
  "name": "Básica",
  "is_active": true
}
```

### AcademicGrade (Grado Académico)

Además de `academic_sublevel` (ID), la respuesta incluye `academic_level_name` (resuelto vía propiedad del modelo):

| Campo                 | Tipo     | Descripción                                                   |
| :-------------------- | :------- | :------------------------------------------------------------ |
| `academic_level_name` | `string` | Nombre del nivel académico (`academic_sublevel.academic_level.name`) |

```json
{
  "id": 3,
  "academic_sublevel": 1,
  "academic_level_name": "Educación General Básica",
  "name": "5to Grado",
  "sequence_order": 5,
  "is_active": true
}
```

---

## Seguridad y Control de Acceso

1.  **Omisión de Permisos**: Los usuarios con `is_superuser=True` omiten toda validación de permiso.
2.  **Mecanismo de Verificación**: Todos los ViewSets aplican `IsAuthenticated` + `HasPermission`. Esta clase mapea la acción DRF (`list`, `create`, `destroy`, etc.) al código de permiso en `action_permissions`.


---

## Estado de Pruebas y Cobertura (Testing Status)

El módulo cuenta con **6 archivos de prueba** que suman **71 pruebas unitarias y de integración**. Todas pasan bajo `--settings=config.settings.test` (SQLite).

| Archivo                        | Tests | Cobertura                                                |
| :----------------------------- | :---: | :------------------------------------------------------- |
| `test_models.py`               |   4   | Creación, fechas, representación de `SchoolYear`         |
| `test_repositories.py`         |  18   | CRUD de `SchoolYearRepository` y `SectionRepository`     |
| `test_services.py`             |   8   | Servicios: validación de fechas, solapamiento, ciclo actual |
| `test_api.py`                  |   9   | Integración HTTP de `SchoolYear` + `Section`             |
| `test_api_gaps.py`             |   7   | Modelos `AcademicLevel`/`AcademicGrade`, RBAC dinámico   |
| `test_api_permissions.py`      |  25   | RBAC: 401/403/200 para cada ViewSet + superusuario       |

### Escenarios Cubiertos

- **Modelos**: Integridad de `SchoolYear`, `AcademicLevel`, `AcademicSublevel` y `AcademicGrade`.
- **Repositorios**: CRUD, filtros por año/grado, borrado físico vs lógico.
- **Servicios**: Validación transaccional de solapamiento, fechas invertidas, ciclo activo, borrado lógico.
- **API**: Listados, creación, edición, detalle de todos los ViewSets.
- **RBAC**: Pruebas automatizadas de 401 (no autenticado), 403 (sin permiso) y 200/201 (con permiso) para cada endpoint, incluyendo bypass de superusuario.

---

## Notas Arquitectónicas


- **No existe una entidad `Institution`** en este módulo. La gestión institucional se realiza a través de `SchoolYear` (años escolares).
- **`AcademicGrade.academic_level`** es una propiedad del modelo que resuelve el nivel desde `academic_sublevel.academic_level`. No es un campo directo en BD.
- **`AcademicSublevel`** reemplazó al antiguo campo `sublevel` (CharField con choices) de `AcademicGrade`, permitiendo una estructura jerárquica más flexible.
- **Los nombres de campo `is_active`** (no `active`) se usan consistentemente en todos los modelos para el borrado lógico.
- **`Section`** tiene tanto borrado físico (`DELETE`) como lógico (`POST /soft-delete/`). `SchoolYear` solo soporta borrado lógico vía `DELETE`.
- **`code` añadido a `AcademicLevel`, `AcademicGrade` y `Section`**: cada entidad ahora tiene un campo `code` único (`CharField(20)`, `unique=True`) para identificar de forma canónica cada registro (ej. `SEC`, `5TO_EGB`, `2024-8A`).
- **`TimeStampedModel` mixin**: `SchoolYear` y `AcademicSublevel` heredan ahora de `TimeStampedModel` (definido en `apps/core/models/base.py`), el cual provee automáticamente los campos `created_at` y `updated_at`.
