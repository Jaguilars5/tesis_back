# Documento de Especificación de Requisitos del Sistema (SRS)

## Sistema de Gestión Académica — Backend

**Versión:** 1.0.0  
**Fecha:** 2026-06-09  
**Estado:** Derivado del código fuente implementado

---

## Índice

1. [Resumen General del Sistema](#1-resumen-general-del-sistema)
2. [Requisitos Funcionales](#2-requisitos-funcionales)
3. [Requisitos No Funcionales](#3-requisitos-no-funcionales)
4. [Entidades y Modelos de Datos](#4-entidades-y-modelos-de-datos)
5. [Integraciones y Dependencias Externas](#5-integraciones-y-dependencias-externas)
6. [Flujos Principales Detectados](#6-flujos-principales-detectados)

---

## 1. Resumen General del Sistema

El **Sistema de Gestión Académica** es una plataforma backend RESTful diseñada para la administración integral de instituciones educativas. Proporciona infraestructura para la gestión de usuarios, roles y permisos (IAM); estructura institucional y académica (años escolares, niveles, grados, secciones, materias); registro y seguimiento de estudiantes con matrícula y representantes; calificaciones estructuradas en bloques de evaluación con actividades, indicadores y procesos de recuperación; asistencia diaria; incidentes de conducta y evaluaciones socioemocionales; analítica de riesgo académico con modelos de machine learning para alertas tempranas; y sincronización offline-first con dispositivos móviles.

El sistema está desarrollado sobre **Django 4.2** y **Django REST Framework**, con **PostgreSQL** como base de datos, **Redis** como caché y broker de mensajería, **Celery** para tareas asíncronas, y empaquetado en contenedores **Docker**.

---

## 2. Requisitos Funcionales

### Módulo: Núcleo del Sistema (Core)

**RF-01 — Formato de respuesta estandarizado**  
Todas las respuestas JSON de la API deben seguir la estructura `{"ok": bool, "data": mixed, "msg": string}`. El `StandardResponseRenderer` se encarga de envolver automáticamente las respuestas. Las respuestas exitosas (`<400`) retornan `ok=true`; las respuestas de error (`>=400`) retornan `ok=false`.  
**Módulo:** `apps.core.api.renderers`  
**Reglas:** Las respuestas ya formateadas no se reenvuelven. Los errores de validación retornan los detalles en `data` y un mensaje genérico en `msg`.

**RF-02 — Manejo global de excepciones**  
Todas las excepciones no controladas de DRF deben ser capturadas por un manejador global que las envuelva en el formato `{ok, data, msg}`. Las excepciones no reconocidas por DRF (código 500) retornan un mensaje de error interno del servidor.  
**Módulo:** `apps.core.api.exceptions`

**RF-03 — Paginación estándar de listados**  
Todos los endpoints de listado deben utilizar paginación con 20 elementos por página, configurable mediante el parámetro `?page_size=` (máximo 100). La respuesta paginada incluye `count`, `next`, `previous` y `results`.  
**Módulo:** `apps.core.api.pagination`

**RF-04 — Seguridad a nivel de fila (Row-Level Security)**  
El sistema debe filtrar automáticamente los querysets según el rol del usuario autenticado, garantizando que ningún usuario acceda a datos fuera de su ámbito relacional. Existen cuatro manejadores de roles:  
- **ESTUDIANTE**: Solo accede a sus propios datos (notas, asistencia, incidentes, evaluaciones). Bloqueado de alertas tempranas y puntajes de riesgo.  
- **REPRESENTANTE**: Accede a sus propios datos y a los datos de los estudiantes que representa, incluyendo alertas tempranas.  
- **DOCENTE**: Accede a sus propios datos y a los datos de los estudiantes en las secciones que tiene asignadas. Requiere perfil `Person`.  
- **CONSEJERO**: Acceso de lectura institucional completo a estudiantes, comportamiento y analítica.  
Los superusuarios y usuarios con categoría `ADMIN` bypassan todos los filtros. Los catálogos públicos (tipos de documento, años escolares, materias, etc.) son accesibles para todos los roles autenticados.  
**Módulo:** `apps.core.api.filters`, `apps.core.api.role_handlers`

**RF-05 — Bitácora de auditoría**  
El sistema debe registrar en una bitácora centralizada (`AuditLog`) cada creación, modificación, eliminación o recuperación de registros, incluyendo el usuario que realizó la acción, el modelo afectado, el ID del registro, los cambios en formato JSON, la dirección IP y el user-agent.  
**Módulo:** `apps.core.models.audit_log`

**RF-06 — Generación idempotente de catálogos del sistema**  
El sistema debe proveer un comando de gestión (`seed_catalogs`) que siembre 132 registros en 25+ catálogos del sistema de forma idempotente (tipos de documento, estados de asistencia, tipos de calificación, escalas cualitativas, tipos de período, tipos de actividad, tipos de evaluación, estados de promoción, tipos de recuperación, tipos de ausencia, tipos de incidente, habilidades socioemocionales, materias, tipos de alerta, niveles de urgencia, factores de riesgo, operaciones de sincronización, estados de sincronización, niveles académicos, estados de matrícula, motivos de retiro, zonas residenciales, tipos de necesidad especial, parentescos, severidades, áreas socioemocionales, niveles de desarrollo, días de la semana, subniveles académicos).  
**Módulo:** `apps.core.management.commands.seed_catalogs`

**RF-07 — Headers de seguridad en respuestas HTTP**  
Todas las respuestas HTTP deben incluir los siguientes headers de seguridad: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy: camera=(), microphone=(), geolocation=()`.  
**Módulo:** `apps.core.middleware.security`

**RF-08 — Documentación OpenAPI 3.0**  
El sistema debe exponer documentación OpenAPI 3.0 completa en tres formatos: schema JSON (`/api/schema/`), Swagger UI (`/api/docs/`) y ReDoc (`/api/redoc/`), todos públicos (sin autenticación). Además, se debe generar documentación por módulo individual en las rutas `/api/schema/{modulo}/`, `/api/docs/{modulo}/` y `/api/redoc/{modulo}/`.  
**Módulo:** `config.urls`, `drf-spectacular`

**RF-09 — Esquema OpenAPI con formato de respuesta estándar**  
La generación del esquema OpenAPI debe documentar correctamente que todas las respuestas 2xx siguen el formato `{ok, data, msg}`.  
**Módulo:** `apps.core.api.schema`

---

### Módulo: Identidad y Acceso (IAM)

**RF-10 — Autenticación JWT**  
El sistema debe permitir autenticación mediante tokens JWT (Bearer). Los usuarios deben poder obtener un par access/refresh token mediante `POST /api/iam/login/` (público). Los access tokens tienen una duración configurable (por defecto 15 minutos). Los refresh tokens tienen una duración configurable (por defecto 7 días) y deben rotarse automáticamente al usarlos, invalidando el token anterior.  
**Módulo:** `apps.iam.api.views`, `apps.iam.api.urls`  
**Reglas:** El login es por **username** (autogenerado). El endpoint de refresh es público (requiere refresh token válido).

**RF-11 — Gestión de usuarios (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/iam/users/`) para la administración de usuarios del sistema, con las operaciones: listar, consultar, crear, actualizar y eliminar (desactivación lógica). Se debe soportar búsqueda por username, nombres, apellidos, email y número de documento. Adicionalmente, debe exponer acciones personalizadas para cambiar contraseña (`/users/{id}/change-password/`), consultar permisos (`/users/{id}/permissions/`) y buscar usuarios (`/users/search/`).  
**Módulo:** `apps.iam.api.views.UserViewSet`  
**Permisos:** `iam.view_user`, `iam.create_user`, `iam.update_user`, `iam.delete_user`

**RF-12 — Gestión de roles (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/iam/roles/`) para la administración de roles del sistema, con acciones personalizadas para agregar permiso (`/roles/{id}/add-permission/`), remover permiso (`/roles/{id}/remove-permission/`) y asignar permisos múltiples (`/roles/{id}/assign-permissions/`).  
**Módulo:** `apps.iam.api.views.RoleViewSet`  
**Permisos:** `iam.view_role`, `iam.create_role`, `iam.update_role`, `iam.delete_role`

**RF-13 — Gestión de permisos (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/iam/permissions/`) para la administración de permisos, con acciones personalizadas para creación masiva (`/permissions/bulk-create/`) y consulta por módulo (`/permissions/by-module/`).  
**Módulo:** `apps.iam.api.views.PermissionViewSet`  
**Permisos:** `iam.view_permission`, `iam.create_permission`, `iam.update_permission`, `iam.delete_permission`

**RF-14 — Generación idempotente de permisos y roles**  
El sistema debe proveer un comando de gestión (`seed_permissions`) que cree o actualice los permisos (200+) y roles predefinidos con sus asignaciones de permisos de forma idempotente. Los roles predefinidos son: ESTUDIANTE (14 permisos), REPRESENTANTE (18 permisos), DOCENTE (51 permisos), DIRECTOR (100+ permisos), RECTOR (17 permisos), CONSEJERO (26 permisos).  
**Módulo:** `apps.iam.management.commands.seed_permissions`

**RF-15 — Generación automática de username**  
El sistema debe generar automáticamente el username de un usuario a partir de sus nombres y apellidos, usando el formato `{primera_letra_nombre}{primer_apellido}`, con numeración autoincremental en caso de duplicados.  
**Módulo:** `apps.iam.models.user.User.generate_username`

**RF-16 — Validación de permisos por usuario**  
El modelo `User` debe implementar un método `has_perm(permission_code)` que verifique si el usuario tiene un permiso específico a través de la cadena `User → UserRole → Role → RolePermission → Permission`. Los superusuarios deben bypassar todas las verificaciones de permisos.  
**Módulo:** `apps.iam.models.user.User`

**RF-17 — Categorización de usuarios por rol**  
El modelo `User` debe exponer una propiedad `user_category` que mapee el código del rol del usuario a una categoría (`ESTUDIANTE`, `REPRESENTANTE`, `DOCENTE`, `ADMIN`, `SIN_ROL`/`OTRO`) para su uso en el filtro de seguridad a nivel de fila.  
**Módulo:** `apps.iam.models.user.User`

**RF-18 — Control de permisos en ViewSets**  
Todos los ViewSets deben utilizar una clase de permiso `HasPermission` que lea el diccionario `action_permissions` del ViewSet y verifique que el usuario tenga el permiso correspondiente a la acción (`list`, `create`, `retrieve`, `update`, `partial_update`, `destroy`). Los superusuarios deben bypassar todas las verificaciones.  
**Módulo:** `apps.core.api.permissions`

---

### Módulo: Personas (People)

**RF-19 — Gestión de personas (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/people/persons/`) para la administración de personas, incluyendo datos básicos: nombres, apellidos, tipo y número de documento, fecha de nacimiento, email y teléfono.  
**Módulo:** `apps.people.api.views.PersonViewSet`  
**Permisos:** `people.view_person`, `people.create_person`, `people.update_person`, `people.delete_person`

**RF-20 — Gestión de tipos de documento (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/people/document-types/`) para el catálogo de tipos de documento de identidad.  
**Módulo:** `apps.people.api.views.DocumentTypeViewSet`  
**Permisos:** `people.view_document_type`, `people.create_document_type`, `people.update_document_type`, `people.delete_document_type`

---

### Módulo: Instituciones (Institutions)

**RF-21 — Gestión de años escolares (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/institutions/school-year/`) para la administración de años escolares, con validación de fechas (inicio anterior a fin) y detección de conflictos de fechas con otros años escolares. Soporta desactivación lógica.  
**Módulo:** `apps.institutions.api.views.SchoolYearViewSet`  
**Permisos:** `institutions.view_school_year`, `institutions.create_school_year`, `institutions.update_school_year`, `institutions.destroy_school_year`

**RF-22 — Gestión de niveles académicos (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/institutions/academic-levels/`) para la administración de niveles académicos (ej: "Educación General Básica", "Bachillerato").  
**Módulo:** `apps.institutions.api.views.AcademicLevelViewSet`  
**Permisos:** `institutions.view_academic_level`, `institutions.create_academic_level`, `institutions.update_academic_level`, `institutions.delete_academic_level`

**RF-23 — Gestión de subniveles académicos (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/institutions/academic-sublevel/`) para la administración de subniveles dentro de un nivel académico (ej: "Básica Elemental" dentro de EGB).  
**Módulo:** `apps.institutions.api.views.AcademicSublevelViewSet`  
**Permisos:** `institutions.view_academic_sublevel`, `institutions.create_academic_sublevel`, `institutions.update_academic_sublevel`, `institutions.delete_academic_sublevel`

**RF-24 — Gestión de grados académicos (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/institutions/academic-grades/`) para la administración de grados o cursos (ej: "5to EGB", "1ro Bachillerato"), con orden secuencial.  
**Módulo:** `apps.institutions.api.views.AcademicGradeViewSet`  
**Permisos:** `institutions.view_academic_grade`, `institutions.create_academic_grade`, `institutions.update_academic_grade`, `institutions.delete_academic_grade`

**RF-25 — Gestión de secciones/paralelos (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/institutions/section/`) para la administración de secciones (paralelos), que combinan año escolar, grado y paralelo. Cada sección tiene una capacidad máxima de estudiantes. Soporta desactivación lógica mediante acción `soft-delete`.  
**Módulo:** `apps.institutions.api.views.SectionViewSet`  
**Permisos:** `institutions.view_section`, `institutions.create_section`, `institutions.update_section`, `institutions.delete_section`

---

### Módulo: Académico (Academic)

**RF-26 — Gestión de materias (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/academic/subject/`) para el catálogo de materias del pensum. Soporta desactivación lógica.  
**Módulo:** `apps.academic.api.views.SubjectViewSet`  
**Permisos:** `academic.view_subject`, `academic.create_subject`, `academic.update_subject`, `academic.delete_subject`

**RF-27 — Gestión de períodos académicos (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/academic/academic-period/`) para la administración de períodos académicos dentro de un año escolar (ej: "Primer Quimestre", "Segundo Parcial"). Los períodos pueden tener un período padre (jerarquía).  
**Módulo:** `apps.academic.api.views.AcademicPeriodViewSet`  
**Permisos:** `academic.view_period`, `academic.create_period`, `academic.update_period`, `academic.delete_period`

**RF-28 — Gestión de tipos de período (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/academic/period-types/`) para el catálogo de tipos de período académico.  
**Módulo:** `apps.academic.api.views.PeriodTypeViewSet`  
**Permisos:** `academic.view_period_type`, `academic.create_period_type`, `academic.update_period_type`, `academic.delete_period_type`

**RF-29 — Configuración de materias por grado (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/academic/subject-academic-configs/`) para configurar qué materias se dictan en cada grado, con horas semanales y orden pedagógico.  
**Módulo:** `apps.academic.api.views.SubjectAcademicConfigViewSet`  
**Permisos:** `academic.view_subject_config`, `academic.create_subject_config`, `academic.update_subject_config`, `academic.delete_subject_config`

**RF-30 — Oferta de materias por sección (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/academic/subject-offerings/`) para la oferta concreta de materias en secciones específicas durante un año escolar.  
**Módulo:** `apps.academic.api.views.SubjectOfferingViewSet`  
**Permisos:** `academic.view_subject_offering`, `academic.create_subject_offering`, `academic.update_subject_offering`, `academic.delete_subject_offering`

**RF-31 — Asignación de docentes a materias y secciones (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/academic/teacher-subject-section/`) para la asignación de docentes (usuarios) a ofertas de materia, definiendo quién dicta qué en cada sección.  
**Módulo:** `apps.academic.api.views.TeacherSubjectSectionViewSet`  
**Permisos:** `academic.view_teacher_subject`, `academic.create_teacher_subject`, `academic.update_teacher_subject`, `academic.delete_teacher_subject`

**RF-32 — Gestión de horarios académicos (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/academic/class-schedule/`) para la administración de horarios de clase: día, hora de inicio, hora de fin, aula y edificio para cada oferta de materia.  
**Módulo:** `apps.academic.api.views.ClassScheduleViewSet`  
**Permisos:** `academic.view_class_schedule`, `academic.create_class_schedule`, `academic.update_class_schedule`, `academic.delete_class_schedule`

**RF-33 — Gestión de proyectos interdisciplinarios (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/academic/interdisciplinary-projects/`) para la administración de proyectos que integran varias materias, con título, fechas, rúbricas y puntajes máximos para producto y presentación.  
**Módulo:** `apps.academic.api.views.InterdisciplinaryProjectViewSet`  
**Permisos:** `academic.view_interdisciplinary_project`, `academic.create_interdisciplinary_project`, `academic.update_interdisciplinary_project`, `academic.delete_interdisciplinary_project`

**RF-34 — Gestión de materias de proyectos (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/academic/subject-projects/`) para la tabla intermedia que conecta proyectos interdisciplinarios con las materias participantes y asigna un docente responsable.  
**Módulo:** `apps.academic.api.views.SubjectProjectViewSet`  
**Permisos:** `academic.view_subject_project`, `academic.create_subject_project`, `academic.update_subject_project`, `academic.delete_subject_project`

**RF-35 — Gestión de días de la semana (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/academic/day-of-week/`) para el catálogo de días de la semana.  
**Módulo:** `apps.academic.api.views.DayOfWeekViewSet`  
**Permisos:** `academic.view_day_of_week`, `academic.create_day_of_week`, `academic.update_day_of_week`, `academic.delete_day_of_week`

---

### Módulo: Estudiantes (Students)

**RF-36 — Gestión de estudiantes (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/students/student/`) para la administración de fichas estudiantiles, incluyendo: código único de estudiante, zona residencial, distancia al colegio, necesidades educativas especiales. Debe soportar acciones personalizadas para listar estudiantes por sección (`/student/by-section/`), buscar (`/student/search/`) y consultar representantes (`/student/{id}/representatives/`). La eliminación es lógica (desactivación).  
**Módulo:** `apps.students.api.views.StudentViewSet`  
**Permisos:** `students.view_student`, `students.create_student`, `students.update_student`, `students.delete_student`, `students.view_relationship`

**RF-37 — Gestión de matrículas (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/students/enrollments/`) para la administración de matrículas, que conectan un estudiante con una sección durante un año escolar. Debe soportar acciones personalizadas para retirar estudiante (`/enrollments/{id}/withdraw/`), transferir estudiante (`/enrollments/{id}/transfer/`), listar por sección (`/enrollments/by-section/`) y consultar por estudiante (`/enrollments/by-student/`).  
**Módulo:** `apps.students.api.views.EnrollmentViewSet`  
**Permisos:** `students.view_enrollment`, `students.create_enrollment`, `students.update_enrollment`, `students.delete_enrollment`, `students.withdraw_student`, `students.transfer_student`

**Reglas de negocio de matrícula:**
- No se permite matricular un estudiante si ya tiene una matrícula activa.
- No se permite matricular en una sección que ha alcanzado su capacidad máxima.
- Al retirar un estudiante, se requiere especificar el motivo de retiro.
- Al transferir, se valida la capacidad de la nueva sección.

**RF-38 — Gestión de representantes de estudiantes (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/students/student-representative/`) para la administración de la relación entre estudiantes y sus representantes legales, incluyendo parentesco, si es el representante principal, si puede recoger al estudiante, si es contacto de emergencia y si recibe notificaciones. Debe soportar acciones personalizadas para establecer representante principal (`set_primary/`) y desvincular (`{id}/unlink/`).  
**Módulo:** `apps.students.api.views.StudentRepresentativeViewSet`  
**Permisos:** `students.view_relationship`, `students.create_relationship`, `students.update_relationship`, `students.delete_relationship`

**RF-39 — Consulta de estados de matrícula (solo lectura)**  
El sistema debe exponer un ViewSet de solo lectura (`/api/students/enrollment-statuses/`) para consultar el catálogo de estados de matrícula.  
**Módulo:** `apps.students.api.views.EnrollmentStatusViewSet`  
**Permisos:** `students.view_enrollment_status`

---

### Módulo: Calificaciones (Grading)

**RF-40 — Gestión de notas de actividad (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/grading/student-notes/`) para el registro de calificaciones de estudiantes en actividades evaluativas. Soporta calificación numérica y cualitativa, con validación de que la nota no exceda el puntaje máximo de la actividad. Normaliza calificaciones a base 10.  
**Módulo:** `apps.grading.api.views.StudentNoteViewSet`  
**Permisos:** `grading.view_note`, `grading.create_note`, `grading.update_note`, `grading.delete_note`

**RF-41 — Gestión de bloques de evaluación (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/grading/evaluation-blocks/`) para la administración de bloques evaluativos dentro de un período y materia, con tipo de evaluación (formativa/sumativa/diagnóstica) y ponderación porcentual.  
**Módulo:** `apps.grading.api.views.EvaluationBlockViewSet`  
**Permisos:** `grading.view_evaluation_macro`, `grading.create_evaluation_macro`, `grading.update_evaluation_macro`, `grading.delete_evaluation_macro`

**RF-42 — Gestión de componentes de bloque (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/grading/block-components/`) para los componentes dentro de un bloque evaluativo, con ponderación interna.  
**Módulo:** `apps.grading.api.views.BlockComponentViewSet`  
**Permisos:** `grading.view_evaluation_criteria`, `grading.create_evaluation_criteria`, `grading.update_evaluation_criteria`, `grading.delete_evaluation_criteria`

**RF-43 — Gestión de indicadores de componente (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/grading/component-indicators/`) para los indicadores de logro dentro de un componente, con ponderación interna.  
**Módulo:** `apps.grading.api.views.ComponentIndicatorViewSet`  
**Permisos:** `grading.view_evaluation_subcriteria`, `grading.create_evaluation_subcriteria`, `grading.update_evaluation_subcriteria`, `grading.delete_evaluation_subcriteria`

**RF-44 — Gestión de actividades evaluativas (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/grading/evaluative-activities/`) para las actividades evaluativas concretas creadas por el docente (tareas, exámenes, lecciones), con título, puntaje máximo, fecha de entrega y tipo de actividad.  
**Módulo:** `apps.grading.api.views.EvaluativeActivityViewSet`  
**Permisos:** `grading.view_class_assignment`, `grading.create_class_assignment`, `grading.update_class_assignment`, `grading.delete_class_assignment`

**RF-45 — Consulta de historial de cambios de calificaciones (solo lectura)**  
El sistema debe exponer un ViewSet de solo lectura (`/api/grading/grade-history/`) para consultar el historial de cambios realizados a las calificaciones, incluyendo valor anterior, nuevo valor, usuario que lo modificó, motivo y origen (manual/recuperación/importación/sincronización).  
**Módulo:** `apps.grading.api.views.GradeChangeHistoryViewSet`  
**Permisos:** `grading.view_grade_history`

**RF-46 — Gestión de resúmenes de calificaciones por período (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/grading/period-grade-summaries/`) para los resúmenes consolidados de calificaciones de un estudiante en una materia durante un período, incluyendo promedios formativo, sumativo y final truncado, estado de promoción y si requiere recuperación.  
**Módulo:** `apps.grading.api.views.PeriodGradeSummaryViewSet`  
**Permisos:** `grading.view_grade_summary`, `grading.create_grade_summary`, `grading.update_grade_summary`, `grading.delete_grade_summary`

**RF-47 — Gestión de procesos de recuperación (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/grading/recovery-processes/`) para los procesos de recuperación académica, incluyendo plan de refuerzo, objetivos, notas de refuerzo y mejora, y notificación a la familia.  
**Módulo:** `apps.grading.api.views.RecoveryProcessViewSet`  
**Permisos:** `grading.view_recovery_process`, `grading.create_recovery_process`, `grading.update_recovery_process`, `grading.delete_recovery_process`

**RF-48 — Gestión de notas de proyectos interdisciplinarios (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/grading/project-notes/`) para las calificaciones de estudiantes en proyectos interdisciplinarios, incluyendo nota del producto, de la presentación y nota final.  
**Módulo:** `apps.grading.api.views.ProjectNoteViewSet`  
**Permisos:** `grading.view_project_note`, `grading.create_project_note`, `grading.update_project_note`, `grading.delete_project_note`

**RF-49 — Cálculo de promedios ponderados por bloque y período**  
El sistema debe calcular automáticamente el promedio ponderado de un bloque de evaluación usando la jerarquía de pesos: actividades → indicadores → componentes → bloques. Debe también calcular el promedio de período como el ponderado de todos los bloques activos.  
**Módulo:** `apps.grading.services.evaluation_service.EvaluationService`

**RF-50 — Cálculo de resumen de calificaciones del período**  
El sistema debe calcular y persistir el `PeriodGradeSummary` para cada combinación de estudiante, materia y período, determinando el estado de promoción basado en si la nota final es >= 7.00.  
**Módulo:** `apps.grading.services.grade_calculation_service.GradeCalculationService`

**RF-51 — Gestión de informes de aprendizaje (CRUD)**  
El sistema debe exponer un ViewSet para la administración de informes de aprendizaje integrales por estudiante y período, incluyendo promedios, tasa de asistencia, escala de conducta, observaciones y recomendaciones. **[PARCIAL]** — El serializer existe pero no se ha verificado su registro en el router.  
**Módulo:** `apps.grading.api.serializers.LearningReportSerializer`, model `LearningReport`

**RF-52 — Gestión de sesiones de refuerzo (CRUD)**  
El sistema debe modelar sesiones individuales de refuerzo dentro de un proceso de recuperación, registrando fecha, duración, temas cubiertos y asistencia del estudiante. **[PARCIAL]** — El modelo y serializer existen.  
**Módulo:** `apps.grading.models.recovery_session.RecoverySession`

**RF-53 — Catálogos de calificaciones (CRUD)**  
El sistema debe exponer ViewSets para los siguientes catálogos: tipos de calificación (`/api/grading/grade-types/`), escalas cualitativas (`/api/grading/qualitative-scales/`), tipos de evaluación (`/api/grading/evaluation-types/`), tipos de actividad (`/api/grading/activity-types/`), estados de promoción (`/api/grading/promotion-statuses/`), tipos de proceso de recuperación (`/api/grading/recovery-process-types/`).  
**Módulo:** `apps.grading.api.views` (6 ViewSets)

---

### Módulo: Asistencia (Attendance)

**RF-54 — Gestión de asistencia (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/attendance/attendances/`) para el registro de asistencia de estudiantes a clases. Cada registro vincula un estudiante (vía matrícula), una clase (vía TeacherSubjectSection), una fecha y un estado de asistencia. Soporta tipo de ausencia y observaciones. La operación es upsert por clave única (estudiante, clase, fecha).  
**Módulo:** `apps.attendance.api.views.AttendanceViewSet`  
**Permisos:** `attendance.view_attendance`, `attendance.create_attendance`, `attendance.update_attendance`, `attendance.delete_attendance`

**RF-55 — Catálogos de asistencia (CRUD)**  
El sistema debe exponer ViewSets para los catálogos: estados de asistencia (`/api/attendance/attendance-statuses/`) con clasificación positiva/negativa, y tipos de ausencia (`/api/attendance/absence-types/`).  
**Módulo:** `apps.attendance.api.views` (2 ViewSets)  
**Permisos:** `attendance.view_attendance_status`, `attendance.create_attendance_status`, `attendance.update_attendance_status`, `attendance.delete_attendance_status`, y análogos para `absence_type`

---

### Módulo: Comportamiento (Behavior)

**RF-56 — Gestión de incidentes de conducta (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/behavior/conduct-incidents/`) para el registro de incidentes de conducta de estudiantes, incluyendo fecha, tipo, severidad, descripción, acciones tomadas y notificación a la familia. Soporta asignación automática de tipo de incidente mediante una propiedad `category`.  
**Módulo:** `apps.behavior.api.views.ConductIncidentViewSet`  
**Permisos:** `behavior.view_conduct_incident`, `behavior.create_conduct_incident`, `behavior.update_conduct_incident`, `behavior.delete_conduct_incident`

**RF-57 — Gestión de evaluaciones de conducta (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/behavior/behavior-evaluations/`) para las evaluaciones integrales de conducta por estudiante y período, con cálculo automático de escala cualitativa basado en reglas y posibilidad de anulación manual.  
**Módulo:** `apps.behavior.api.views.BehaviorEvaluationViewSet`  
**Permisos:** `behavior.view_behavior_evaluation`, `behavior.create_behavior_evaluation`, `behavior.update_behavior_evaluation`, `behavior.delete_behavior_evaluation`

**RF-58 — Gestión de evaluaciones de habilidades socioemocionales (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/behavior/skill-evaluations/`) para la evaluación de habilidades socioemocionales específicas por estudiante y período, asignando una escala cualitativa.  
**Módulo:** `apps.behavior.api.views.SkillEvaluationViewSet`  
**Permisos:** `behavior.view_skill_evaluation`, `behavior.create_skill_evaluation`, `behavior.update_skill_evaluation`, `behavior.delete_skill_evaluation`

**RF-59 — Gestión de evaluaciones diagnósticas socioemocionales (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/behavior/diagnostic-evaluations/`) para evaluaciones diagnósticas socioemocionales que evalúan un área específica y asignan un nivel de desarrollo, con hallazgos y recomendaciones.  
**Módulo:** `apps.behavior.api.views.DiagnosticEvaluationViewSet`  
**Permisos:** `behavior.view_diagnostic_evaluation`, `behavior.create_diagnostic_evaluation`, `behavior.update_diagnostic_evaluation`, `behavior.delete_diagnostic_evaluation`

**RF-60 — Catálogos de comportamiento (CRUD)**  
El sistema debe exponer ViewSets para los catálogos: tipos de incidente (`/api/behavior/incident-types/`) y habilidades socioemocionales (`/api/behavior/socioemotional-skills/`).  
**Módulo:** `apps.behavior.api.views` (2 ViewSets)

---

### Módulo: Analítica y Riesgo (Analytics)

**RF-61 — Gestión de puntajes de riesgo estudiantil (lectura + cálculo)**  
El sistema debe exponer un ViewSet (`/api/analytics/student-risk-scores/`) para consultar los puntajes de riesgo calculados por estudiante y período, con etiqueta de riesgo (Bajo/Medio/Alto) y versión del modelo. Debe exponer acciones personalizadas para calcular riesgo individual (`/student-risk-scores/{id}/calculate/`) y cálculo por lote (`/student-risk-scores/batch-calculate/`).  
**Módulo:** `apps.analytics.api.views.StudentRiskScoreViewSet`  
**Permisos:** `analytics.view_risk_score`

**RF-62 — Gestión de instantáneas de métricas estudiantiles (solo lectura)**  
El sistema debe exponer un ViewSet de solo lectura (`/api/analytics/feature-snapshots/`) para consultar las instantáneas de métricas que sirven como entrada para el modelo de riesgo. Las métricas incluyen: tasa de asistencia, atrasos, ausencias justificadas/injustificadas, promedios formativo/sumativo normalizados, pendiente de tendencia de notas, materias reprobadas, puntaje de conducta, incidentes graves, proporción de notificaciones familiares, promedio de período anterior, brecha edad-grado, repetición, necesidades especiales y alertas activas.  
**Módulo:** `apps.analytics.api.views.StudentFeatureSnapshotViewSet`  
**Permisos:** `analytics.view_feature_snapshot`

**RF-63 — Gestión de alertas tempranas (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/analytics/early-alerts/`) para la administración de alertas tempranas generadas automática o manualmente para estudiantes, incluyendo tipo de alerta, nivel de urgencia, descripción y estado de atención. Debe exponer una acción personalizada para marcar como atendida (`/early-alerts/{id}/mark-attended/`).  
**Módulo:** `apps.analytics.api.views.EarlyAlertViewSet`  
**Permisos:** `analytics.view_early_alert`, `analytics.create_early_alert`, `analytics.update_early_alert`, `analytics.delete_early_alert`

**RF-64 — Dashboard de analítica**  
El sistema debe exponer un ViewSet (`/api/analytics/dashboard/`) con acciones personalizadas de solo lectura para: vista general del período (`/dashboard/overview/`), distribución de riesgo por grado (`/dashboard/risk-distribution/`), estudiantes en riesgo (`/dashboard/students-at-risk/`), exportación CSV (`/dashboard/export-csv/`) y resumen por sección (`/dashboard/section-summary/`).  
**Módulo:** `apps.analytics.api.views.DashboardViewSet`  
**Permisos:** `analytics.view_risk_score`

**RF-65 — Generación automática de alertas tempranas**  
El sistema debe ejecutar una tarea programada (vía Celery) que evalúe estudiantes activos y genere alertas tempranas basadas en reglas de negocio: asistencia baja (<70%), múltiples materias reprobadas (>=2), e incidentes graves recurrentes (>=2).  
**Módulo:** `apps.analytics.services.early_alert_service.EarlyAlertService`, tarea Celery `auto_generate_early_alerts`

**RF-66 — Modelo de machine learning para riesgo académico**  
El sistema debe implementar un modelo de clasificación basado en `GradientBoostingClassifier` con 16 características para predecir el riesgo académico de estudiantes. Debe incluir un comando de gestión para entrenar el modelo (`train_risk_model`) que persiste el modelo entrenado en `risk_model.joblib`.  
**Módulo:** `apps.analytics.ml.train_model.RiskModelTrainer`

**RF-67 — Clustering de estudiantes**  
El sistema debe implementar clustering de estudiantes usando KMeans (con StandardScaler) para identificar grupos con perfiles de riesgo similares.  
**Módulo:** `apps.analytics.services.student_clustering_service.StudentClusteringService`, tarea Celery `run_student_clustering`

**RF-68 — Exportación CSV de datos analíticos**  
El sistema debe generar archivos CSV exportables con datos de riesgo y asistencia por período académico.  
**Módulo:** `apps.analytics.services.csv_export_service.CSVExportService`

**RF-69 — Catálogos de analítica (CRUD)**  
El sistema debe exponer ViewSets para los catálogos: tipos de alerta (`/api/analytics/alert-types/`), niveles de urgencia (`/api/analytics/urgency-levels/`), factores de riesgo (`/api/analytics/risk-factors/`) y factores de riesgo por estudiante (`/api/analytics/student-risk-factors/`).  
**Módulo:** `apps.analytics.api.views` (4 ViewSets)

---

### Módulo: Configuración (Configuration)

**RF-70 — Gestión de configuración del sistema (CRUD)**  
El sistema debe exponer un ViewSet (`/api/configuration/system-config/`) para la administración de configuraciones como pares clave-valor, con `lookup_field = "key"`.  
**Módulo:** `apps.configuration.api.views.SystemConfigViewSet`  
**Permisos:** `configuration.view_systemconfig`, `configuration.create_systemconfig`, `configuration.update_systemconfig`, `configuration.delete_systemconfig`

---

### Módulo: Integración (Integration)

**RF-71 — Cola de sincronización (CRUD)**  
El sistema debe exponer un ViewSet completo (`/api/integration/sync-queue/`) para la administración de la cola de operaciones pendientes de sincronizar. Cada entrada representa un cambio (INSERT/UPDATE/DELETE) en una tabla específica, con payload de datos y mecanismo de idempotencia mediante clave SHA-256. Al crear un ítem, se dispara automáticamente una tarea Celery para procesarlo.  
**Módulo:** `apps.integration.api.views.SyncQueueViewSet`  
**Permisos:** `integration.view_syncqueue`, `integration.create_syncqueue`, `integration.update_syncqueue`, `integration.delete_syncqueue`

**RF-72 — Sincronización por lotes (push/pull)**  
El sistema debe exponer endpoints públicos (autenticados) para sincronización masiva: `POST /api/integration/sync/push/` para enviar un lote de operaciones desde el cliente, y `GET /api/integration/sync/pull/` para obtener cambios desde una marca de tiempo.  
**Módulo:** `apps.integration.api.views`

**RF-73 — Procesamiento asíncrono de cola de sincronización**  
El sistema debe ejecutar una tarea periódica de Celery cada 5 minutos (`process_pending_sync_batch`) que procese todos los ítems pendientes en la cola de sincronización, y una tarea individual (`process_sync_queue_item`) con reintentos (máx. 3, retraso 60s) para cada ítem.  
**Módulo:** `apps.integration.tasks.sync_tasks`

**RF-74 — Estrategias de resolución de conflictos**  
El sistema debe implementar tres estrategias de resolución de conflictos para sincronización:  
- **LAST_WRITE_WINS**: Para tablas de bajo riesgo (attendance, student_note, evaluative_activity, conduct_incident).  
- **SERVER_WINS**: Para tablas críticas (user, person, student, enrollment_status, sync_queue).  
- **MANUAL**: Para enrollment (requiere intervención humana).  
**Módulo:** `apps.integration.services.conflict_resolver.ConflictResolutionStrategy`

**RF-75 — Modelo sincronizable (mixin abstracto)**  
El sistema debe proveer un modelo abstracto `SyncableModel` que agregue campos para sincronización offline-first a cualquier modelo: UUID único, estado de sincronización (PENDING/PROCESSING/SYNCED/ERROR/CONFLICT), versión de sincronización, marca de tiempo de última sincronización, origen del dispositivo, y campos de resolución de conflictos. Los modelos que lo implementan son: `Enrollment`, `EvaluativeActivity`, `StudentNote`, `ProjectNote`, `RecoveryProcess`, `RecoverySession`, `LearningReport`, `Attendance`, `BehaviorEvaluation`, `ConductIncident`, `DiagnosticEvaluation`, `SkillEvaluation`, `EarlyAlert`.  
**Módulo:** `apps.integration.models.syncable_mixin.SyncableModel`

**RF-76 — Control de versiones de esquema de sincronización**  
El sistema debe mantener un registro de versiones de esquema por modelo sincronizable para garantizar compatibilidad entre servidor y clientes móviles.  
**Módulo:** `apps.integration.models.sync_schema_version.SyncSchemaVersion`

**RF-77 — Manejadores de sincronización por modelo**  
El sistema debe implementar manejadores de sincronización específicos para cada modelo sincronizable, registrados mediante el decorador `@register_sync_handler(source_table)`. Los manejadores implementan lógica de inserción, actualización (con resolución de conflictos) y eliminación. Existen manejadores para: student_note, project_note, evaluative_activity, recovery_process, recovery_session, learning_report, enrollment, attendance, conduct_incident, behavior_evaluation, skill_evaluation, diagnostic_evaluation, early_alert.  
**Módulo:** Múltiples archivos `tasks.py` en cada app.

---

## 3. Requisitos No Funcionales

**RNF-01 — Seguridad: Autenticación JWT**  
Categoría: Seguridad  
El sistema debe utilizar autenticación mediante tokens JWT (JSON Web Tokens) con algoritmo HS256. Los access tokens deben tener una vida útil de 15 minutos (configurable vía `JWT_ACCESS_EXPIRE_MINUTES`) y los refresh tokens de 7 días (configurable vía `JWT_REFRESH_EXPIRE_DAYS`). La rotación de refresh tokens debe estar activada, invalidando el token anterior al emitir uno nuevo. Los tokens se transmiten mediante el header `Authorization: Bearer <token>`.  
**Implementación:** `config.settings.base`, `rest_framework_simplejwt`

**RNF-02 — Seguridad: Contraseñas**  
Categoría: Seguridad  
El sistema debe aplicar las siguientes políticas de contraseñas: longitud mínima de 12 caracteres, prohibición de contraseñas similares al usuario, prohibición de contraseñas comunes y prohibición de contraseñas numéricas.  
**Implementación:** `config.settings.base.AUTH_PASSWORD_VALIDATORS`

**RNF-03 — Seguridad: Headers de respuesta**  
Categoría: Seguridad  
Todas las respuestas HTTP deben incluir headers de seguridad: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy: camera=(), microphone=(), geolocation=()`.  
**Implementación:** `apps.core.middleware.SecurityHeadersMiddleware`

**RNF-04 — Seguridad: Configuración de producción**  
Categoría: Seguridad  
En entorno de producción, el sistema debe forzar HTTPS (redirección SSL), cookies de sesión y CSRF seguras, HSTS por 1 año con includeSubDomains y preload, filtro XSS del navegador, prevención de sniffing de contenido, y header `X-Frame-Options: DENY`.  
**Implementación:** `config.settings.production`

**RNF-05 — Seguridad: Rate limiting**  
Categoría: Seguridad / Rendimiento  
El sistema debe aplicar límites de tasa: 100 requests/día para usuarios anónimos, 1000 requests/día para usuarios autenticados, y 10 requests/hora para el endpoint de login.  
**Implementación:** `config.settings.base.REST_FRAMEWORK.DEFAULT_THROTTLE_RATES`

**RNF-06 — Seguridad: Control de acceso basado en roles (RBAC)**  
Categoría: Seguridad  
Todos los endpoints (excepto login y refresh) deben requerir autenticación JWT y un permiso específico. El sistema debe implementar 6 roles predefinidos con diferentes conjuntos de permisos: ESTUDIANTE (14), REPRESENTANTE (18), DOCENTE (51), DIRECTOR (100+), RECTOR (17), CONSEJERO (26). Los superusuarios deben tener acceso completo sin restricción.  
**Implementación:** `apps.core.api.permissions.HasPermission`, `apps.iam.management.commands.seed_permissions`

**RNF-07 — Seguridad: Aislamiento de datos por rol (RLS)**  
Categoría: Seguridad  
El sistema debe garantizar que cada usuario solo acceda a los datos que le corresponden según su rol institucional, mediante un filtro global de seguridad a nivel de fila implementado como backend de filtro de DRF.  
**Implementación:** `apps.core.api.filters.RoleBasedFilterBackend`, `apps.core.api.role_handlers`

**RNF-08 — Seguridad: Bitácora de auditoría**  
Categoría: Seguridad  
El sistema debe mantener un registro auditable de todas las operaciones de creación, modificación y eliminación de datos, incluyendo quién realizó la operación, qué datos cambiaron (en formato JSON), la dirección IP y el user-agent.  
**Implementación:** `apps.core.models.audit_log.AuditLog`

**RNF-09 — Seguridad: CORS**  
Categoría: Seguridad  
El sistema debe permitir peticiones cross-origin desde `http://localhost:3000` (desarrollo) y desde los orígenes configurados en la variable de entorno `CORS_ALLOWED_ORIGINS` (producción), con soporte para credenciales.  
**Implementación:** `django-cors-headers`, `config.settings`

**RNF-10 — Rendimiento: Paginación**  
Categoría: Rendimiento  
Todos los endpoints de listado deben implementar paginación con un tamaño de página predeterminado de 20 elementos, configurable mediante el parámetro `?page_size=` con un máximo de 100 elementos por página.  
**Implementación:** `apps.core.api.pagination.StandardResultsSetPagination`

**RNF-11 — Rendimiento: Caché con Redis**  
Categoría: Rendimiento  
El sistema debe utilizar Redis como motor de caché para mejorar el rendimiento de consultas frecuentes.  
**Implementación:** `django-redis`, `config.settings`

**RNF-12 — Rendimiento: Tareas asíncronas con Celery**  
Categoría: Rendimiento  
El sistema debe procesar tareas pesadas (cálculo de riesgo, procesamiento de sincronización, clustering) de forma asíncrona mediante Celery, utilizando Redis como broker de mensajería. Las tareas deben tener un límite de tiempo de 30 minutos y seguimiento de inicio.  
**Implementación:** `config.celery`, `config.settings.base.CELERY_*`

**RNF-13 — Rendimiento: Tarea periódica de sincronización**  
Categoría: Rendimiento  
El sistema debe ejecutar una tarea Celery programada cada 5 minutos para procesar los ítems pendientes en la cola de sincronización.  
**Implementación:** `config.settings.base.CELERY_BEAT_SCHEDULE`

**RNF-14 — Disponibilidad: Contenedores Docker**  
Categoría: Disponibilidad / Despliegue  
El sistema debe empaquetarse en contenedores Docker para garantizar la consistencia del entorno de ejecución. Debe incluir servicios para: aplicación web (Gunicorn/Django runserver), base de datos PostgreSQL, Redis, worker Celery y monitor Flower.  
**Implementación:** `Dockerfile`, `docker-compose.yml`

**RNF-15 — Disponibilidad: Health checks**  
Categoría: Disponibilidad  
Los servicios de base de datos y Redis deben incluir health checks para garantizar que están operativos antes de que la aplicación web y los workers intenten conectarse.  
**Implementación:** `docker-compose.yml`

**RNF-16 — Mantenibilidad: Arquitectura en capas**  
Categoría: Mantenibilidad  
El sistema debe organizarse en una arquitectura de cuatro capas: `models/` → `repositories/` → `services/` → `api/`. Todas las consultas ORM deben residir exclusivamente en la capa de repositorios. Las vistas y servicios no deben contener consultas directas a `Model.objects`.  
**Implementación:** Múltiples módulos, patrón consistente en todas las apps.

**RNF-17 — Mantenibilidad: Formato de respuesta consistente**  
Categoría: Mantenibilidad  
Todas las respuestas de la API deben seguir el formato `{"ok": bool, "data": mixed, "msg": string}` para garantizar la consistencia entre backend y frontend.  
**Implementación:** `apps.core.api.renderers.StandardResponseRenderer`, `apps.core.api.exceptions.custom_exception_handler`

**RNF-18 — Mantenibilidad: Documentación OpenAPI**  
Categoría: Mantenibilidad  
El sistema debe generar documentación OpenAPI 3.0 automáticamente a partir de los ViewSets, accesible en formato schema JSON, Swagger UI y ReDoc, tanto global como por módulo individual. La documentación debe reflejar el formato de respuesta estándar `{ok, data, msg}`.  
**Implementación:** `drf-spectacular`, `config.urls`

**RNF-19 — Mantenibilidad: Separación de entornos**  
Categoría: Mantenibilidad  
El sistema debe soportar múltiples entornos de configuración (base, local, producción, pruebas) mediante herencia de settings, cargando variables de entorno desde un archivo `.env`.  
**Implementación:** `config.settings/` (base.py, local.py, production.py, test.py)

**RNF-20 — Portabilidad: PostgreSQL como base de datos principal**  
Categoría: Portabilidad  
El sistema debe utilizar PostgreSQL como motor de base de datos en los entornos de desarrollo local y producción. En el entorno de pruebas debe utilizar SQLite para simplificar la ejecución.  
**Implementación:** `config.settings/local.py` (PostgreSQL), `config.settings/production.py` (PostgreSQL), `config.settings/test.py` (SQLite)

**RNF-21 — Portabilidad: Configuración mediante variables de entorno**  
Categoría: Portabilidad  
Todas las configuraciones sensibles y específicas del entorno (claves secretas, credenciales de base de datos, URLs de Redis) deben cargarse desde variables de entorno mediante un archivo `.env` cargado con `python-dotenv`.  
**Implementación:** `config.settings.base`, `python-dotenv`

**RNF-22 — Pruebas: Suite de pruebas automatizadas**  
Categoría: Calidad  
El sistema debe contar con una suite de pruebas automatizadas (569+ tests) que cubra modelos, servicios, repositorios y API de todos los módulos. Las pruebas deben utilizar `django.test.TestCase` y DRF `APIClient` con `force_authenticate` (no JWT). El entorno de pruebas debe usar SQLite, Celery eager, caché en memoria y hasher MD5.  
**Implementación:** `config.settings.test`, tests distribuidos en todos los módulos.

**RNF-23 — Pruebas: Cobertura de seguridad**  
Categoría: Calidad  
El sistema debe incluir pruebas específicas de seguridad que verifiquen: autenticación (401 sin token, 403 sin permiso), permisos RBAC para todos los módulos, headers de seguridad, rate limiting, validación de contraseñas, configuración JWT y generación de esquema OpenAPI.  
**Implementación:** `apps.core.tests` (14 archivos de prueba)

**RNF-24 — Internacionalización**  
Categoría: Usabilidad  
El sistema debe configurarse con locale `es-ec` (Español - Ecuador) y zona horaria `America/Guayaquil`.  
**Implementación:** `config.settings.base`

---

## 4. Entidades y Modelos de Datos

A continuación se listan las 58 tablas del sistema organizadas por módulo, con sus relaciones principales.

### 4.1 Core (2 tablas)

| Tabla | Descripción | Relaciones |
|-------|-------------|------------|
| `TimeStampedModel` | Abstracto: `created_at`, `updated_at` | Heredado por ~45 modelos |
| `AuditLog` | Bitácora de auditoría: usuario, acción, modelo, registro, cambios JSON, IP, user-agent | FK → `iam.User` |

### 4.2 IAM — Identidad y Acceso (5 tablas)

| Tabla | Descripción | Relaciones |
|-------|-------------|------------|
| `User` | Usuario del sistema: username, email, password, is_active, is_staff, is_superuser | 1:1 → `people.Person` |
| `Role` | Rol: name, code, description, is_active | M:M → `Permission` vía `RolePermission` |
| `Permission` | Permiso: code (`<mod>.<action>`), description, module | M:M → `Role` vía `RolePermission` |
| `UserRole` | Asignación rol-usuario: assigned_at, expires_at | FK → `User`, FK → `Role` |
| `RolePermission` | Asignación permiso-rol | FK → `Role`, FK → `Permission` |

### 4.3 People — Personas (2 tablas)

| Tabla | Descripción | Relaciones |
|-------|-------------|------------|
| `Person` | Persona natural: document_number (único), names, last_names, birth_date, email, phone | FK → `DocumentType`; 1:1 → `User`, `Student` |
| `DocumentType` | Tipo de documento: code (único), name | Relacionado con `Person` |

### 4.4 Institutions — Instituciones (5 tablas)

| Tabla | Descripción | Relaciones |
|-------|-------------|------------|
| `SchoolYear` | Año escolar: name, start_date, end_date, is_active | Raíz de estructura académica |
| `AcademicLevel` | Nivel académico: code, name, is_active | Padre de `AcademicSublevel` |
| `AcademicSublevel` | Subnivel: code, name, description, is_active | FK → `AcademicLevel`; padre de `AcademicGrade` |
| `AcademicGrade` | Grado: code, name, sequence_order, is_active | FK → `AcademicSublevel` |
| `Section` | Sección/paralelo: code, parallel, capacity, is_active | FK → `SchoolYear`, FK → `AcademicGrade` |

### 4.5 Academic — Académico (10 tablas)

| Tabla | Descripción | Relaciones |
|-------|-------------|------------|
| `PeriodType` | Tipo de período: code, name | FK → `AcademicPeriod` |
| `AcademicPeriod` | Período académico: code, name, start_date, end_date, is_regular_period | FK → `SchoolYear`, FK → `PeriodType`, auto-FK `parent_period` |
| `Subject` | Materia: name, code (único), is_active | Tabla base del catálogo |
| `SubjectAcademicConfig` | Config. materia-grado: weekly_hours, pedagogical_order, is_required | FK → `Subject`, FK → `AcademicGrade` |
| `SubjectOffering` | Oferta de materia: is_active | FK → `SchoolYear`, FK → `Section`, FK → `SubjectAcademicConfig` |
| `TeacherSubjectSection` | Asignación docente: is_active | FK → `User`, FK → `SubjectOffering` |
| `DayOfWeek` | Día de semana: code, name | FK → `ClassSchedule` |
| `ClassSchedule` | Horario: start_time, end_time, classroom, building | FK → `SubjectOffering`, FK → `DayOfWeek` |
| `InterdisciplinaryProject` | Proyecto interdisciplinario: title, description, fechas, rúbricas, puntajes | FK → `AcademicPeriod`; M:M → `SubjectOffering` vía `SubjectProject` |
| `SubjectProject` | Materia de proyecto | FK → `InterdisciplinaryProject`, FK → `SubjectOffering`, FK → `User` |

### 4.6 Students — Estudiantes (9 tablas)

| Tabla | Descripción | Relaciones |
|-------|-------------|------------|
| `Student` | Estudiante: student_code (único), distance_to_school_km, has_special_needs, is_active | 1:1 → `Person`; FK → `ResidentialZone`, FK → `SpecialNeedsType` |
| `ResidentialZone` | Zona residencial: code, name | Catálogo |
| `SpecialNeedsType` | Tipo de NEE: code, name | Catálogo |
| `EnrollmentStatus` | Estado de matrícula: code (ACT/RET/TRS/SUS/GRA), name | Catálogo |
| `WithdrawalReason` | Motivo de retiro: code, name | Catálogo |
| `Kinship` | Parentesco: code, name | Catálogo |
| `Enrollment` | Matrícula: enrollment_date, withdrawal_date, is_repeat | FK → `Student`, FK → `Section`, FK → `SchoolYear`, FK → `EnrollmentStatus`, FK → `WithdrawalReason` |
| `EnrollmentHistory` | Historial de matrícula: previous_status, new_status, change_reason, effective_date | FK → `Enrollment`, FK → `EnrollmentStatus` (x2), FK → `User` |
| `StudentRepresentative` | Representante: is_primary, can_pickup, emergency_contact, receives_notifications | FK → `Student`, FK → `Person`, FK → `Kinship` |

### 4.7 Grading — Calificaciones (19 tablas)

| Tabla | Descripción | Relaciones |
|-------|-------------|------------|
| `GradeType` | Tipo de calificación | M:M → `AcademicSublevel` |
| `QualitativeScale` | Escala cualitativa: code, name, numeric_equivalence | Relacionada con `QualitativeScaleSublevel` |
| `QualitativeScaleSublevel` | Puente escala-subnivel | FK → `QualitativeScale`, FK → `AcademicSublevel` |
| `EvaluationType` | Tipo de evaluación: code (FORMATIVA/SUMATIVA/DIAGNÓSTICA) | Catálogo |
| `ActivityType` | Tipo de actividad | Catálogo |
| `PromotionStatus` | Estado de promoción (approved/failed/recovery) | Catálogo |
| `RecoveryProcessType` | Tipo de recuperación: allows_improvement_eval, allows_suppletorio, min_grade_to_access, max_recovery_attempts | Catálogo |
| `EvaluationBlock` | Bloque de evaluación: weight_percentage | FK → `AcademicPeriod`, FK → `SubjectOffering`, FK → `EvaluationType` |
| `BlockComponent` | Componente de bloque: internal_weight | FK → `EvaluationBlock` |
| `ComponentIndicator` | Indicador de componente: internal_weight | FK → `BlockComponent` |
| `EvaluativeActivity` | Actividad evaluativa: title, max_score, due_date, is_interdisciplinary_project | FK → `ComponentIndicator`, FK → `TeacherSubjectSection`, FK → `ActivityType` |
| `StudentNote` | Nota de actividad: grading_mode, numeric_score, manually_overridden, teacher_observation | FK → `Enrollment`, FK → `EvaluativeActivity`, FK → `GradeType`, FK → `QualitativeScale`, FK → `User` (x2) |
| `GradeChangeHistory` | Historial de cambio: previous_score, new_score, reason, reason_code, origin | FK → `StudentNote`, FK → `User` (x2), FK → `QualitativeScale` (x2) |
| `PeriodGradeSummary` | Resumen de período: promedios, requires_recovery, promotion_status | FK → `Enrollment`, FK → `SubjectOffering`, FK → `AcademicPeriod`, FK → `QualitativeScale`, FK → `PromotionStatus`, FK → `User` (x2) |
| `LearningReport` | Informe de aprendizaje: promedios, attendance_rate, general_observations, recommendations, is_final | FK → `Enrollment`, FK → `AcademicPeriod`, FK → `QualitativeScale`, FK → `User` (x3) |
| `ProjectNote` | Nota de proyecto: product_score, presentation_score, final_score | FK → `Enrollment`, FK → `InterdisciplinaryProject` |
| `RecoveryProcess` | Proceso de recuperación: notas, fechas, plan, objectives, observations, family_notified | FK → `PeriodGradeSummary`, FK → `SubjectOffering`, FK → `User`, FK → `RecoveryProcessType` |
| `RecoverySession` | Sesión de refuerzo: session_date, duration_minutes, topics_covered, student_present | FK → `RecoveryProcess` |
| `RecoveryProcessHistory` | Historial de recuperación: action, notas, estados | FK → `RecoveryProcess`, FK → `PromotionStatus`, FK → `User` |

### 4.8 Attendance — Asistencia (3 tablas)

| Tabla | Descripción | Relaciones |
|-------|-------------|------------|
| `AttendanceStatus` | Estado de asistencia: code, name, tipo (POSITIVO/NEGATIVO) | Catálogo |
| `AbsenceType` | Tipo de ausencia: code, name | Catálogo |
| `Attendance` | Registro de asistencia: attendance_date, observation | FK → `Enrollment`, FK → `TeacherSubjectSection`, FK → `AcademicPeriod`, FK → `AttendanceStatus`, FK → `AbsenceType`, FK → `User` (x2) |

### 4.9 Behavior — Comportamiento (9 tablas)

| Tabla | Descripción | Relaciones |
|-------|-------------|------------|
| `IncidentType` | Tipo de incidente: code, name | Catálogo |
| `Severity` | Severidad: code, name, numeric_level | Catálogo |
| `SocioemotionalSkill` | Habilidad socioemocional: code, name | Catálogo |
| `SocioemotionalArea` | Área socioemocional: code, name | Catálogo |
| `DevelopmentLevel` | Nivel de desarrollo: code, name | Catálogo |
| `ConductIncident` | Incidente de conducta: incident_date, description, actions_taken, family_notified | FK → `Enrollment`, FK → `AcademicPeriod`, FK → `IncidentType`, FK → `Severity`, FK → `User` (x3) |
| `SkillEvaluation` | Evaluación de habilidad: observation, evaluation_date | FK → `Enrollment`, FK → `AcademicPeriod`, FK → `SocioemotionalSkill`, FK → `QualitativeScale` |
| `BehaviorEvaluation` | Evaluación de conducta: general_observation, override_reason, evaluation_date, approval_date | FK → `Enrollment`, FK → `AcademicPeriod`, FK → `QualitativeScale` (x2), FK → `User` (x3) |
| `DiagnosticEvaluation` | Evaluación diagnóstica: findings_description, application_date, recommendations | FK → `Enrollment`, FK → `AcademicPeriod`, FK → `User`, FK → `SocioemotionalArea`, FK → `DevelopmentLevel` |

### 4.10 Analytics — Analítica (8 tablas)

| Tabla | Descripción | Relaciones |
|-------|-------------|------------|
| `AlertType` | Tipo de alerta: code, name | Catálogo |
| `UrgencyLevel` | Nivel de urgencia: code, name | Catálogo |
| `RiskFactor` | Factor de riesgo: code, name, description | Catálogo |
| `StudentFeatureSnapshot` | Instantánea de métricas: 16 campos numéricos | FK → `Enrollment`, FK → `AcademicPeriod` |
| `StudentRiskScore` | Puntaje de riesgo: risk_score, risk_label, model_version | FK → `Enrollment`, FK → `AcademicPeriod` |
| `StudentRiskFactor` | Factor de riesgo detallado: contribution_weight | FK → `StudentRiskScore`, FK → `RiskFactor` |
| `EarlyAlert` | Alerta temprana: description, attended, response_actions | FK → `Enrollment`, FK → `AcademicPeriod`, FK → `AlertType`, FK → `UrgencyLevel`, FK → `User` |
| `DashboardMetric` | Métrica de dashboard: metric_type, metric_value (JSON) | FK → `AcademicPeriod`, FK → `Section`, FK → `AcademicGrade` |

### 4.11 Configuration — Configuración (1 tabla)

| Tabla | Descripción | Relaciones |
|-------|-------------|------------|
| `SystemConfig` | Configuración clave-valor: key (único), value, description | Ninguna |

### 4.12 Integration — Integración (4 tablas + 1 mixin)

| Tabla | Descripción | Relaciones |
|-------|-------------|------------|
| `SyncableModel` (abstracto) | Mixin: uuid, sync_status, sync_version, synced_at, device_origin, conflict_resolved, conflict_notes | Heredado por 13 modelos |
| `SyncOperation` | Operación: code (INSERT/UPDATE/DELETE) | Catálogo |
| `SyncStatus` | Estado de sincronización: code (PENDIENTE/PROCESANDO/SINCRONIZADO/ERROR/CONFLICTO) | Catálogo |
| `SyncSchemaVersion` | Versión de esquema: model_name, schema_version, fields_hash, min_client_version | Independiente |
| `SyncQueue` | Cola de sincronización: idempotency_key (SHA-256), source_table, record_uuid, payload, previous_state, attempts, last_error | FK → `User`, FK → `SyncOperation`, FK → `SyncStatus`, FK → `User` (resolved_by) |

---

## 5. Integraciones y Dependencias Externas

### 5.1 Librerías y Frameworks Python

| Librería | Versión | Propósito |
|----------|---------|-----------|
| Django | >=4.2, <5.0 | Framework web principal |
| djangorestframework | >=3.14.0 | Framework REST API |
| djangorestframework-simplejwt | >=5.3.1 | Autenticación JWT |
| django-cors-headers | >=4.3.0 | Soporte CORS para frontend separado |
| django-redis | >=5.4.0 | Caché distribuida con Redis |
| django-filter | >=24.3 | Filtrado y búsqueda en endpoints |
| drf-spectacular | >=0.27.0 | Generación de esquema OpenAPI 3.0 |
| python-dotenv | >=1.0.1 | Carga de variables de entorno |
| psycopg2-binary | >=2.9.9 | Conexión a PostgreSQL |
| gunicorn | >=21.0.0 | Servidor WSGI para producción |
| celery | >=5.3.0 | Cola de tareas asíncronas |
| redis | >=5.0.0 | Cliente Redis para Python |
| bcrypt | >=4.2.1 | Hashing de contraseñas |
| flower | >=2.0.0 | Monitor web de Celery |
| coverage | >=7.4.0 | Medición de cobertura de pruebas |
| numpy | >=1.26.0 | Cómputo numérico (analítica) |
| pandas | >=2.2.0 | Manipulación de datos (analítica) |
| scikit-learn | >=1.4.0 | Machine learning (clasificación y clustering) |
| joblib | >=1.3.0 | Persistencia de modelos ML |

### 5.2 Servicios de Infraestructura

| Servicio | Tecnología | Propósito |
|----------|------------|-----------|
| Base de datos | PostgreSQL 15 | Almacenamiento persistente de datos |
| Caché / Broker | Redis 7 | Caché de Django + broker de Celery |
| Worker asíncrono | Celery 5 | Procesamiento de tareas en segundo plano |
| Monitor Celery | Flower 2 | Monitoreo visual de workers y tareas |
| Contenedores | Docker + Docker Compose | Aislamiento y despliegue de servicios |
| Servidor WSGI | Gunicorn 21 | Servidor de aplicaciones para producción |

### 5.3 Integraciones del Sistema

| Integración | Tipo | Descripción |
|-------------|------|-------------|
| Frontend (SPA) | CORS | Frontend en `localhost:3000` se comunica vía API REST con JWT |
| Clientes móviles | Sync API | Sincronización offline-first mediante endpoints push/pull con cola de operaciones y resolución de conflictos |
| Documentación API | OpenAPI 3.0 | Schema JSON, Swagger UI y ReDoc públicos en `/api/schema/`, `/api/docs/`, `/api/redoc/` |
| pgAdmin | Interfaz web | Administración visual de PostgreSQL en puerto 5037 (solo Docker) |

---

## 6. Flujos Principales Detectados

### Flujo 1: Autenticación y Control de Acceso

```
[Cliente] → POST /api/iam/login/ (username + password)
  → Valida credenciales → Genera access_token (15 min) + refresh_token (7 días)
  → Retorna tokens + datos del usuario (rol, permisos)
  
[Cliente] → POST /api/iam/refresh/ (refresh_token)
  → Valida refresh_token → Genera nuevo par de tokens (rotación)
  → Invalida refresh_token anterior
  
[Cliente] → GET /api/* (Authorization: Bearer access_token)
  → Valida token JWT → Verifica autenticación
  → Verifica permiso específico vía HasPermission + action_permissions
  → Aplica filtro de seguridad a nivel de fila según rol
  → Retorna datos en formato {ok, data, msg}
```

### Flujo 2: Registro de Estudiante con Matrícula

```
[Admin] → Crea Person (RF-19) → Crea Student (RF-36) con código único
  → Valida uniqueness de documento y código
  → Asocia representantes (RF-38) con parentesco
  
[Admin] → POST /api/students/enrollments/ (RF-37)
  → Valida que no exista matrícula activa
  → Valida capacidad de la sección
  → Crea Enrollment con estado ACT (Activo)
  → Crea EnrollmentHistory con cambio de estado
```

### Flujo 3: Evaluación Académica (Ciclo Completo)

```
[Configuración] → Crear EvaluationBlock (RF-41) con ponderación
  → Crear BlockComponent (RF-42) con peso interno
  → Crear ComponentIndicator (RF-43) con peso interno
  
[Docente] → Crear EvaluativeActivity (RF-44) con puntaje máximo
  → Crear StudentNote (RF-40) para cada estudiante
    → Valida nota ≤ max_score de la actividad
    → Normaliza calificación a base 10
  
[Sistema] → Calcular promedio del bloque (EvaluationService)
  → Ponderación: actividad → indicador → componente → bloque
  → Calcular PeriodGradeSummary (GradeCalculationService)
    → Promedio ponderado de bloques → nota final
    → Si nota final >= 7.00: promovido
    → Si nota final < 7.00: requiere_recuperación = true
  → Persistir GradeChangeHistory en cada modificación
```

### Flujo 4: Recuperación Académica

```
[Docente] → Identifica estudiante con requires_recovery = true
  → Inicia RecoveryProcess (RF-47) con tipo de proceso
    → Establece plan de refuerzo, objetivos, fechas
    → Notifica a la familia (family_notified = true)
  
[Docente] → Registra RecoverySession (RF-52) con temas y asistencia
  → Actualiza notas de refuerzo y/o mejora
  
[Docente/Sistema] → Completa proceso de recuperación
  → Si nota final >= 7.00: actualiza promotion_status a "approved"
  → Registra RecoveryProcessHistory con cada cambio de estado
```

### Flujo 5: Asistencia Diaria

```
[Docente] → POST /api/attendance/attendances/ (RF-54)
  → Para cada estudiante en su sección:
    → Crea/modifica Attendance (upsert por estudiante + materia + fecha)
    → Asigna estado: Presente, Ausente (con tipo), Atraso
    → Opcional: observaciones
  
[Sistema] → Calcula métricas de asistencia para analítica:
  → Tasa de asistencia, atrasos, ausencias justificadas/injustificadas
  → Utilizado en StudentFeatureSnapshot y alertas tempranas
```

### Flujo 6: Gestión de Conducta

```
[Docente/Consejero] → Registra ConductIncident (RF-56)
  → Especifica tipo, severidad, descripción, acciones
  → Opcional: notifica a la familia
  
[Docente/Consejero] → Evalúa habilidades socioemocionales (RF-58)
  → Asigna escala cualitativa por habilidad
  
[Sistema] → Calcula BehaviorEvaluation (RF-57) por período
  → Reglas: mapeo de incidentes y evaluaciones a escala (DA/SA/AC/NA)
  → Permite anulación manual con motivo
  
[Consejero] → Realiza DiagnosticEvaluation socioemocional (RF-59)
  → Evalúa área específica, asigna nivel de desarrollo
  → Documenta hallazgos y recomendaciones
```

### Flujo 7: Analítica de Riesgo y Alertas Tempranas

```
[Programado - Celery] → auto_generate_early_alerts (RF-65)
  → Evalúa todos los estudiantes con matrícula activa
  → Reglas de alerta:
    1. Asistencia < 70% → alerta de ausentismo
    2. >= 2 materias reprobadas → alerta de bajo rendimiento
    3. >= 2 incidentes graves → alerta de conducta
  → Crea EarlyAlert (RF-63) con tipo y urgencia

[Programado - Celery] → calculate_student_academic_risk_task (RF-61)
  → Construye StudentFeatureSnapshot con 16 métricas (RF-62)
  → Aplica modelo GradientBoostingClassifier
  → Calcula StudentRiskScore con etiqueta (Bajo/Medio/Alto)
  
[Consejero] → Consulta Dashboard (RF-64) con distribución de riesgo
  → Filtra estudiantes en riesgo por grado/sección
  → Marca alertas como atendidas con acciones de respuesta
  → Exporta CSV para reportes

[Programado - Celery] → run_student_clustering (RF-67)
  → Clusteriza estudiantes con KMeans (4 clusters)
  → Identifica perfiles de riesgo similares
```

### Flujo 8: Sincronización Offline-First

```
[Dispositivo Móvil] → POST /api/integration/sync/push/ (RF-72)
  → Envía lote de operaciones con payloads
  → Cada operación tiene clave de idempotencia (SHA-256)
  → Se crean SyncQueue items con estado PENDIENTE
  
[Servidor - Celery] → Procesa cola cada 5 minutos (RF-73)
  → Para cada ítem pendiente:
    → Busca handler según source_table
    → Ejecuta handler (INSERT/UPDATE/DELETE)
    → Resuelve conflictos según estrategia:
      - LAST_WRITE_WINS: attendance, student_note, etc.
      - SERVER_WINS: user, person, student, etc.
      - MANUAL: enrollment (marca conflicto)
    → Actualiza estado a PROCESADO o ERROR
  
[Dispositivo Móvil] → GET /api/integration/sync/pull/ (RF-72)
  → Obtiene cambios desde última sincronización
  → Filtra por source_table opcional
  → Actualiza caché local
```

### Flujo 9: Ciclo de Vida de la Matrícula

```
[Registro] → Crear matrícula (estado: ACT - Activo)
  → Valida sin matrícula activa previa
  → Valida cupo en sección
  
[Transferencia] → POST /enrollments/{id}/transfer/ (nueva_sección)
  → Valida cupo en nueva sección
  → Cambia sección de la matrícula
  → Mantiene estado activo
  
[Retiro] → POST /enrollments/{id}/withdraw/ (motivo)
  → Cambia estado a RET (Retirado)
  → Registra fecha y motivo de retiro
  
[Graduación] → Cambio manual a GRA (Graduado)
  → Historial registrado en EnrollmentHistory
```

### Flujo 10: Generación de Informes de Aprendizaje

```
[Sistema] → Crea LearningReport (modelo existente)
  → Agrega promedios formativo, sumativo y final
  → Calcula tasa de asistencia
  → Asigna escala de conducta
  → Incluye observaciones y recomendaciones
  → Marca como final o borrador
  
[Docente/Director] → Aprueba informe (approved_by)
  → Informe disponible para consulta de representantes
```

---

*Fin del documento SRS. Versión 1.0.0 — Derivado del código fuente implementado.*
