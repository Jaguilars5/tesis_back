# Modelo de Datos — Sistema de Gestión Académica

Este documento describe de manera conceptual cada tabla del sistema, qué representa y cómo se relaciona con las demás. Está organizado por módulos (apps) para facilitar su comprensión.

---

## 1. Núcleo del Sistema (`core`)

| Tabla | Nombre en español | ¿Qué es? | ¿Con qué se relaciona? |
|-------|-------------------|----------|------------------------|
| **AuditLog** | Bitácora de Auditoría | Bitácora que registra cada creación, modificación o eliminación de cualquier registro del sistema. Sirve como pista de auditoría para saber quién hizo qué, cuándo y desde dónde. | Se relaciona con `User` (quién realizó la acción). No es crítica para el negocio, es de control. |

Además existe un modelo abstracto llamado `TimeStampedModel` del cual heredan casi todas las tablas del sistema; este simplemente agrega las columnas `created_at` (fecha de creación) y `updated_at` (fecha de última modificación) a cada tabla hija.

---

## 2. Identificación, Acceso y Permisos (`iam`)

| Tabla | Nombre en español | ¿Qué es? | ¿Con qué se relaciona? |
|-------|-------------------|----------|------------------------|
| **User** | Usuario | Usuarios del sistema (docentes, administradores, consejeros, etc.). Cada usuario tiene credenciales de acceso (username, email, password). | Se relaciona 1 a 1 con `Person` (una persona tiene un solo usuario). |
| **Role** | Rol | Roles o perfiles del sistema (DOCENTE, ADMIN, ESTUDIANTE, REPRESENTANTE, etc.). Los roles agrupan permisos. | Se relaciona con `Permission` a través de `RolePermission`. |
| **Permission** | Permiso | Permisos individuales del sistema, ej: `grading.create_note` (crear notas), `iam.view_user` (ver usuarios). | Se relaciona con `Role` a través de `RolePermission`. |
| **RolePermission** | Permiso del Rol | Tabla intermedia que asigna permisos a un rol. Define **qué puede hacer** cada rol. | Conecta `Role` con `Permission` (muchos a muchos). |
| **UserRole** | Rol del Usuario | Tabla intermedia que asigna roles a los usuarios. Define **quién es qué** en el sistema. Un usuario puede tener varios roles. | Conecta `User` con `Role` (muchos a muchos). |

**Regla clave**: Un usuario accede al sistema según los permisos que tenga su rol. Los superusuarios tienen todos los permisos sin restricción.

---

## 3. Personas (`people`)

| Tabla | Nombre en español | ¿Qué es? | ¿Con qué se relaciona? |
|-------|-------------------|----------|------------------------|
| **Person** | Persona | Datos básicos de cualquier persona natural: nombres, apellidos, documento de identidad, fecha de nacimiento, email, teléfono. | Se relaciona con `DocumentType` (tipo de documento). Puede ser estudiante (vía `Student`), representante (vía `StudentRepresentative`), o usuario del sistema (vía `User`). |
| **DocumentType** | Tipo de Documento | Catálogo de tipos de documento de identidad (Cédula, Pasaporte, etc.). | Usada por `Person`. |

---

## 4. Instituciones y Estructura Académica (`institutions`)

| Tabla | Nombre en español | ¿Qué es? | ¿Con qué se relaciona? |
|-------|-------------------|----------|------------------------|
| **SchoolYear** | Año Escolar | Año lectivo o escolar. Ej: "2025-2026". Define el período anual de funcionamiento. | Es la raíz de la estructura académica. Varias tablas dependen de ella. |
| **AcademicLevel** | Nivel Académico | Nivel académico general. Ej: "Educación General Básica", "Bachillerato". | Es el nivel más alto de la jerarquía académica. |
| **AcademicSublevel** | Subnivel Académico | Subnivel dentro de un nivel académico. Ej: "Básica Elemental" (dentro de EGB), "Básica Media". | Pertenece a un `AcademicLevel`. |
| **AcademicGrade** | Grado Académico | Grado o curso específico. Ej: "5to EGB", "1ro Bachillerato". | Pertenece a un `AcademicSublevel`. Tiene un orden secuencial. |
| **Section** | Sección | Sección o paralelo: la combinación de un año escolar + un grado + un paralelo (letra). Ej: "2025-2026 / 5to EGB / A". Tiene una capacidad máxima de estudiantes. | Pertenece a `SchoolYear` y a `AcademicGrade`. |

**Jerarquía**: `SchoolYear` → (contiene) → `Section` → (pertenece a) → `AcademicGrade` → (pertenece a) → `AcademicSublevel` → (pertenece a) → `AcademicLevel`

---

## 5. Académico (`academic`)

| Tabla | Nombre en español | ¿Qué es? | ¿Con qué se relaciona? |
|-------|-------------------|----------|------------------------|
| **PeriodType** | Tipo de Período | Catálogo de tipos de período académico (Quimestre, Parcial, etc.). | Usada por `AcademicPeriod`. |
| **AcademicPeriod** | Período Académico | Período académico dentro de un año escolar. Ej: "Primer Quimestre", "Segundo Parcial". Puede tener un período padre (ej: un parcial dentro de un quimestre). | Pertenece a `SchoolYear` y a `PeriodType`. Puede tener un `parent_period` (autoreferencia). |
| **Subject** | Materia | Materias o asignaturas del pensum. Ej: "Matemáticas", "Lengua y Literatura". | Tabla base del catálogo de materias. |
| **SubjectAcademicConfig** | Configuración de Materia por Grado | Configuración de qué materias se dictan en qué grado, con cuántas horas semanales y en qué orden pedagógico. Ej: "Matemáticas en 5to EGB con 5 horas semanales". | Conecta `Subject` con `AcademicGrade`. |
| **SubjectOffering** | Oferta de Materia | Oferta concreta de una materia en una sección específica durante un año escolar. Ej: "Matemáticas de 5to EGB A en 2025-2026". | Conecta `SubjectAcademicConfig`, `Section` y `SchoolYear`. |
| **TeacherSubjectSection** | Docente-Materia-Sección | Asignación de un docente a una oferta de materia. Define **quién dicta qué** en cada sección. | Conecta `User` (docente) con `SubjectOffering`. |
| **DayOfWeek** | Día de la Semana | Catálogo de días de la semana (Lunes, Martes, etc.). | Usada por `ClassSchedule`. |
| **ClassSchedule** | Horario Académico | Horario de clases: día, hora de inicio, hora de fin, aula y edificio para cada oferta de materia. | Pertenece a `SubjectOffering` y a `DayOfWeek`. |
| **InterdisciplinaryProject** | Proyecto Interdisciplinario | Proyecto interdisciplinario que integra varias materias. Tiene título, fechas, rúbricas y puntajes máximos para producto y presentación. | Pertenece a `AcademicPeriod` y se relaciona con `SubjectOffering` a través de `SubjectProject`. |
| **SubjectProject** | Asignatura del Proyecto | Tabla intermedia que conecta un proyecto interdisciplinario con las materias que participan, y asigna un docente responsable para cada materia. | Conecta `InterdisciplinaryProject` con `SubjectOffering`, e indica el `User` (docente) responsable. |

**Flujo**: `SchoolYear` → `AcademicPeriod` → (contiene) → `InterdisciplinaryProject`.
**Flujo de materias**: `Subject` → `SubjectAcademicConfig` (por grado) → `SubjectOffering` (por sección) → `TeacherSubjectSection` (asignación docente) + `ClassSchedule` (horario).

---

## 6. Estudiantes (`students`)

| Tabla | Nombre en español | ¿Qué es? | ¿Con qué se relaciona? |
|-------|-------------------|----------|------------------------|
| **Student** | Estudiante | Ficha del estudiante con datos específicos: código estudiantil, zona residencial, distancia al colegio, necesidades educativas especiales. | Se relaciona 1 a 1 con `Person`. Se relaciona con `ResidentialZone` y `SpecialNeedsType`. |
| **ResidentialZone** | Zona Residencial | Catálogo de zonas residenciales (Urbana, Rural, etc.). | Usada por `Student`. |
| **SpecialNeedsType** | Tipo de Necesidad Especial | Catálogo de tipos de necesidades educativas especiales (NEE). | Usada por `Student`. |
| **EnrollmentStatus** | Estado de Matrícula | Catálogo de estados de matrícula (Activo, Retirado, Graduado, etc.). | Usada por `Enrollment`. |
| **WithdrawalReason** | Motivo de Retiro | Catálogo de motivos de retiro (Cambio de ciudad, Problemas económicos, etc.). | Usada por `Enrollment`. |
| **Enrollment** | Matrícula | Matrícula: inscripción de un estudiante en una sección durante un año escolar. Es el registro central que conecta al estudiante con toda su actividad académica. | Conecta `Student`, `Section` y `SchoolYear`. Tiene un estado (`EnrollmentStatus`) y opcionalmente un motivo de retiro (`WithdrawalReason`) y año repetido (`SchoolYear`). |
| **EnrollmentHistory** | Historial de Matrícula | Historial de cambios de estado de una matrícula (ej: de Activo a Retirado). Registro de auditoría de la matrícula. | Pertenece a `Enrollment` y registra el `EnrollmentStatus` anterior y nuevo. |
| **Kinship** | Parentesco | Catálogo de tipos de parentesco (Madre, Padre, Tutor, etc.). | Usada por `StudentRepresentative`. |
| **StudentRepresentative** | Relación Estudiante-Representante | Relación entre un estudiante y su representante (persona adulta responsable). Indica el parentesco, si es el representante principal, si puede recoger al estudiante, si es contacto de emergencia, etc. | Conecta `Student` con `Person` (representante), e indica el tipo de `Kinship`. |

**Nota**: Un representante es una `Person` (no necesariamente un `User` del sistema). Un estudiante es un `Student` que a su vez es una `Person`, y puede tener múltiples representantes.

---

## 7. Calificaciones (`grading`)

Es el módulo más grande del sistema. Maneja toda la evaluación académica.

### 7.1 Catálogos

| Tabla | Nombre en español | ¿Qué es? | ¿Con qué se relaciona? |
|-------|-------------------|----------|------------------------|
| **EvaluationType** | Tipo de Evaluación | Tipo de evaluación (Formativa, Sumativa, Diagnóstica). | Usada por `EvaluationBlock`. |
| **ActivityType** | Tipo de Actividad | Tipo de actividad evaluativa (Tarea, Lección, Examen, Taller, etc.). | Usada por `EvaluativeActivity`. |
| **GradeType** | Tipo de Calificación | Tipo de calificación (Parcial, Examen, Deber, etc.). Puede aplicarse a ciertos subniveles académicos. | Se relaciona con `AcademicSublevel` (muchos a muchos). |
| **PromotionStatus** | Estado de Promoción | Estado de promoción (Aprobado, Reprobado, En Recuperación, etc.). | Usada por `PeriodGradeSummary` y `LearningReport`. |
| **QualitativeScale** | Escala Cualitativa | Escala cualitativa de calificación. Ej: "DA" (Destreza Alcanzada) con equivalencia numérica 9.00. | Usada en varias tablas de calificación. |
| **QualitativeScaleSublevel** | Escala Cualitativa por Subnivel | Tabla intermedia que asigna qué escalas cualitativas están disponibles en cada subnivel académico. | Conecta `QualitativeScale` con `AcademicSublevel`. |

### 7.2 Estructura de Evaluación (configuración por período)

| Tabla | Nombre en español | ¿Qué es? | ¿Con qué se relaciona? |
|-------|-------------------|----------|------------------------|
| **EvaluationBlock** | Bloque de Evaluación | Bloque de evaluación: agrupación de componentes evaluativos dentro de un período y materia. Ej: "Bloque Formativo" con 60% de ponderación, "Bloque Sumativo" con 40%. | Pertenece a `AcademicPeriod` y a `SubjectOffering`. Usa `EvaluationType`. |
| **BlockComponent** | Componente de Bloque | Componente dentro de un bloque de evaluación. Ej: dentro del bloque formativo: "Tareas" (30%), "Lecciones" (30%). | Pertenece a `EvaluationBlock`. |
| **ComponentIndicator** | Indicador de Componente | Indicador de logro dentro de un componente. Ej: dentro de "Tareas": "Resuelve problemas de suma" (50%), "Aplica propiedades" (50%). | Pertenece a `BlockComponent`. |

**Jerarquía**: `EvaluationBlock` → `BlockComponent` → `ComponentIndicator`

### 7.3 Actividades y Notas

| Tabla | Nombre en español | ¿Qué es? | ¿Con qué se relaciona? |
|-------|-------------------|----------|------------------------|
| **EvaluativeActivity** | Actividad Evaluativa | Actividad evaluativa concreta creada por el docente: una tarea, un examen, una lección. Tiene título, puntaje máximo, fecha de entrega. | Pertenece a `ComponentIndicator` (el indicador que evalúa) y a `TeacherSubjectSection` (el docente que la crea). Opcionalmente usa `ActivityType`. |
| **StudentNote** | Nota de Actividad | Nota de un estudiante en una actividad evaluativa. Es la tabla de mayor volumen de datos. Puede ser numérica o cualitativa. | Conecta `Enrollment` (el estudiante matriculado) con `EvaluativeActivity`. Usa `GradeType` y opcionalmente `QualitativeScale`. |
| **GradeChangeHistory** | Historial de Cambio de Calificación | Registro de cada cambio que se hace a una nota, incluyendo valor anterior, nuevo valor, quién lo cambió, por qué y desde qué dispositivo. | Pertenece a `StudentNote`. |
| **PeriodGradeSummary** | Resumen de Calificaciones del Período | Resumen de calificaciones de un estudiante en una materia durante un período. Contiene promedios formativo, sumativo y final. Indica si requiere recuperación. | Conecta `Enrollment`, `SubjectOffering` y `AcademicPeriod`. Usa `QualitativeScale` y `PromotionStatus`. |
| **ProjectNote** | Nota de Proyecto | Nota de un estudiante en un proyecto interdisciplinario. Incluye nota del producto, de la presentación y nota final. | Conecta `Enrollment` con `InterdisciplinaryProject`. |
| **LearningReport** | Informe de Aprendizaje | Informe de aprendizaje integral de un estudiante por período. Incluye promedios, tasa de asistencia, escala de conducta, observaciones y recomendaciones. Es el documento final que se entrega a los padres. | Conecta `Enrollment` con `AcademicPeriod`. Usa `QualitativeScale` para conducta. |

### 7.4 Recuperación

| Tabla | Nombre en español | ¿Qué es? | ¿Con qué se relaciona? |
|-------|-------------------|----------|------------------------|
| **RecoveryProcessType** | Tipo de Proceso de Recuperación | Catálogo de tipos de proceso de recuperación (Refuerzo, Supletorio, Evaluación de mejora, etc.). Define reglas como nota mínima para acceder y máximo de intentos. | Usada por `RecoveryProcess`. |
| **RecoveryProcess** | Proceso de Recuperación | Proceso de recuperación para un estudiante que no alcanzó la nota mínima en una materia. Incluye plan de refuerzo, objetivos, fechas, notas de refuerzo y mejora, y si la familia fue notificada. | Pertenece a `PeriodGradeSummary` y a `SubjectOffering`. Gestionado por un `User`. Usa `RecoveryProcessType`. |
| **RecoverySession** | Sesión de Refuerzo | Sesión individual de refuerzo dentro de un proceso de recuperación. Registra fecha, duración, temas cubiertos y si el estudiante asistió. | Pertenece a `RecoveryProcess`. |
| **RecoveryProcessHistory** | Historial de Proceso de Recuperación | Historial de cambios de estado de un proceso de recuperación (Iniciado, Calificación actualizada, Sesión completada, Completado, Cancelado). | Pertenece a `RecoveryProcess`. |

---

## 8. Asistencia (`attendance`)

| Tabla | Nombre en español | ¿Qué es? | ¿Con qué se relaciona? |
|-------|-------------------|----------|------------------------|
| **AttendanceStatus** | Estado de Asistencia | Catálogo de estados de asistencia (Presente, Ausente, Atraso, etc.). Cada estado puede ser positivo o negativo. | Usada por `Attendance`. |
| **AbsenceType** | Tipo de Ausencia | Catálogo de tipos de ausencia (Justificada, Injustificada, Médica, etc.). | Usada por `Attendance`. |
| **Attendance** | Asistencia | Registro de asistencia de un estudiante a una clase en una fecha específica. Indica si estuvo presente, ausente (con tipo de ausencia) o atrasado, con observaciones. | Conecta `Enrollment` (estudiante), `TeacherSubjectSection` (la clase), `AcademicPeriod` y `AttendanceStatus`. Opcionalmente usa `AbsenceType`. |

**Regla**: Un estudiante tiene un registro de asistencia por cada día y cada materia.

---

## 9. Comportamiento (`behavior`)

| Tabla | Nombre en español | ¿Qué es? | ¿Con qué se relaciona? |
|-------|-------------------|----------|------------------------|
| **IncidentType** | Tipo de Incidente | Catálogo de tipos de incidentes de conducta (Disrupción en aula, Acoso, Daños materiales, etc.). | Usada por `ConductIncident`. |
| **Severity** | Severidad | Catálogo de niveles de severidad (Leve, Moderado, Grave). Tiene un nivel numérico para ordenar. | Usada por `ConductIncident`. |
| **ConductIncident** | Incidente de Conducta | Registro de un incidente de conducta de un estudiante. Incluye fecha, tipo, severidad, descripción, acciones tomadas, y si se notificó a la familia. | Pertenece a `Enrollment` y `AcademicPeriod`. Reportado por un `User`. |
| **SocioemotionalArea** | Área Socioemocional | Catálogo de áreas socioemocionales (Autoconocimiento, Empatía, Regulación emocional, etc.). | Usada por `DiagnosticEvaluation`. |
| **DevelopmentLevel** | Nivel de Desarrollo | Catálogo de niveles de desarrollo (Inicial, En Proceso, Alcanzado, etc.). | Usada por `DiagnosticEvaluation`. |
| **DiagnosticEvaluation** | Evaluación Diagnóstica | Evaluación diagnóstica socioemocional de un estudiante. Evalúa un área específica y asigna un nivel de desarrollo, con hallazgos y recomendaciones. | Pertenece a `Enrollment`, `AcademicPeriod` y `SocioemotionalArea`. Aplicada por un `User`. |
| **SocioemotionalSkill** | Habilidad Socioemocional | Catálogo de habilidades socioemocionales específicas (Trabajo en equipo, Comunicación asertiva, etc.). | Usada por `SkillEvaluation`. |
| **SkillEvaluation** | Evaluación de Habilidad | Evaluación de una habilidad socioemocional específica en un estudiante durante un período. Asigna una escala cualitativa. | Pertenece a `Enrollment`, `AcademicPeriod` y `SocioemotionalSkill`. Usa `QualitativeScale`. |
| **BehaviorEvaluation** | Evaluación de Conducta | Evaluación integral de conducta de un estudiante por período. Calcula una escala final (puede ser anulada manualmente por el docente). | Pertenece a `Enrollment` y `AcademicPeriod`. Usa `QualitativeScale` (calculada y final). |

---

## 10. Analítica y Alertas Tempranas (`analytics`)

| Tabla | Nombre en español | ¿Qué es? | ¿Con qué se relaciona? |
|-------|-------------------|----------|------------------------|
| **AlertType** | Tipo de Alerta | Catálogo de tipos de alerta temprana (Bajo rendimiento, Ausentismo, Problemas de conducta, etc.). | Usada por `EarlyAlert`. |
| **UrgencyLevel** | Nivel de Urgencia | Catálogo de niveles de urgencia (Baja, Media, Alta, Crítica). | Usada por `EarlyAlert`. |
| **EarlyAlert** | Alerta Temprana | Alerta temprana generada automática o manualmente para un estudiante. Indica un riesgo potencial (académico, conductual, de asistencia) y si ha sido atendida. | Pertenece a `Enrollment` y `AcademicPeriod`. |
| **RiskFactor** | Factor de Riesgo | Catálogo de factores de riesgo (Asistencia baja, Notas bajas, Incidentes graves, etc.). | Usada por `StudentRiskFactor`. |
| **StudentRiskScore** | Puntaje de Riesgo del Estudiante | Puntaje de riesgo calculado para un estudiante en un período. Incluye el puntaje numérico, una etiqueta (Bajo, Medio, Alto) y la versión del modelo ML usado. | Pertenece a `Enrollment` y `AcademicPeriod`. |
| **StudentRiskFactor** | Factor de Riesgo del Estudiante | Desglose de los factores que contribuyen al puntaje de riesgo de un estudiante, con el peso porcentual de cada factor. | Conecta `StudentRiskScore` con `RiskFactor`. |
| **StudentFeatureSnapshot** | Instantánea de Métricas del Estudiante | Instantánea de todas las métricas de un estudiante en un período, usada como entrada para el modelo de riesgo. Incluye: tasas de asistencia, atrasos, promedios, tendencia de notas, materias reprobadas, incidentes, conducta, etc. | Pertenece a `Enrollment` y `AcademicPeriod`. |
| **DashboardMetric** | Métrica de Dashboard | Métricas pre-calculadas para el dashboard de la institución. Almacena indicadores por período, sección y grado. | Pertenece a `AcademicPeriod`, opcionalmente a `Section` y `AcademicGrade`. |

---

## 11. Configuración (`configuration`)

| Tabla | Nombre en español | ¿Qué es? | ¿Con qué se relaciona? |
|-------|-------------------|----------|------------------------|
| **SystemConfig** | Configuración del Sistema | Almacena configuraciones del sistema como pares clave-valor. Sirve para parametrizar el comportamiento del sistema sin cambiar código. | No se relaciona con otras tablas. |

---

## 12. Integración y Sincronización (`integration`)

Este módulo permite la sincronización de datos con dispositivos móviles (offline-first).

| Tabla | Nombre en español | ¿Qué es? | ¿Con qué se relaciona? |
|-------|-------------------|----------|------------------------|
| **SyncStatus** | Estado de Sincronización | Catálogo de estados de sincronización (Pendiente, Procesando, Sincronizado, Error, Conflicto). | Usada por `SyncQueue`. |
| **SyncOperation** | Operación de Sincronización | Catálogo de operaciones de sincronización (CREAR, ACTUALIZAR, ELIMINAR). | Usada por `SyncQueue`. |
| **SyncSchemaVersion** | Versión de Esquema de Sincronización | Control de versiones de los esquemas de datos para garantizar compatibilidad entre el servidor y los clientes móviles. | Independiente. |
| **SyncQueue** | Cola de Sincronización | Cola de operaciones pendientes de sincronizar. Cada entrada representa un cambio (creación, modificación, eliminación) en una tabla específica, con el payload de datos y el estado de sincronización. | Conecta con `User` (origen), `SyncOperation` y `SyncStatus`. |
| **SyncableModel** (abstracto) | — | Mixin abstracto que agrega UUID, estado de sincronización, versión y control de conflictos a cualquier modelo que herede de él. Lo usan: `Enrollment`, `EvaluativeActivity`, `StudentNote`, `ProjectNote`, `RecoveryProcess`, `RecoverySession`, `LearningReport`, `Attendance`, `BehaviorEvaluation`, `ConductIncident`, `DiagnosticEvaluation`, `SkillEvaluation`, `EarlyAlert`. | Es abstracto, no tiene tabla propia, pero sus campos aparecen en todas las tablas que lo heredan. |

---

## Resumen de Relaciones Clave

```
Person (1:1) → User (acceso al sistema)
Person (1:1) → Student (ficha estudiantil)
Student → Enrollment → Section (matrícula en un paralelo)
Enrollment → EvaluativeActivity → StudentNote (notas)
Enrollment → Attendance (asistencia)
Enrollment → ConductIncident (incidentes de conducta)
Enrollment → BehaviorEvaluation (evaluación de conducta)
Enrollment → LearningReport (informe final)
Enrollment → StudentRiskScore (riesgo académico)
Enrollment → EarlyAlert (alertas tempranas)

Subject → SubjectAcademicConfig → AcademicGrade (materias por grado)
SubjectAcademicConfig → SubjectOffering → Section (materias ofrecidas en cada paralelo)
SubjectOffering → TeacherSubjectSection → User (docente asignado)
SubjectOffering → ClassSchedule (horario)

AcademicPeriod → EvaluationBlock → BlockComponent → ComponentIndicator (estructura evaluativa)
ComponentIndicator → EvaluativeActivity (actividades creadas por el docente)
TeacherSubjectSection → EvaluativeActivity (docente crea actividades)
AcademicPeriod → InterdisciplinaryProject (proyectos interdisciplinarios)
```
