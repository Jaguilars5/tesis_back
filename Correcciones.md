# README - Plan de corrección y rediseño de la base de datos

## 1. Propósito

Este documento define una hoja de ruta técnica para corregir y rediseñar la base de datos de un sistema académico orientado a instituciones educativas ecuatorianas, a partir de un análisis previo del modelo relacional actual [file:1]. El plan organiza las acciones por fases, dependencias y prioridad para reducir riesgo de migración, corregir defectos estructurales y preparar el modelo para operación académica, sincronización offline-first y explotación analítica [file:1].

## 2. Contexto del sistema

La base de datos soporta un sistema académico con módulos de identidad, instituciones, períodos académicos, asignaturas, matrícula, asistencia, calificaciones, conducta, seguimiento socioemocional, alertas tempranas, analítica y sincronización [file:1]. El modelo también intenta cubrir lógica educativa por niveles y subniveles, evaluaciones cualitativas y cuantitativas, procesos de recuperación académica, reportes institucionales y capacidades futuras para detección temprana de riesgo estudiantil [file:1].

## 3. Objetivo del documento

Este README convierte un análisis técnico previo en un plan ejecutable de remediación y rediseño [file:1]. Su finalidad es servir como guía operativa para un equipo técnico que deba intervenir el esquema, migrar datos, reforzar integridad referencial y alinear el modelo con la lógica académica y los requerimientos de escalabilidad del sistema [file:1].

## 4. Resumen de hallazgos

Los hallazgos se concentran en cinco frentes principales [file:1]:

- Problemas de base estructural, como relaciones ambiguas, relaciones declaradas sin campo visible, nulabilidad incorrecta y una dependencia circular entre `AcademicSublevel` y `AcademicGrade` [file:1].
- Problemas de modelado académico, como bloques de evaluación no vinculados a la oferta de asignatura, mezcla de calificación cuantitativa y cualitativa sin discriminación robusta y procesos de recuperación incompletos [file:1].
- Problemas de normalización, como uso de cadenas libres donde deberían existir catálogos o claves foráneas, especialmente en escalas cualitativas, evaluaciones diagnósticas y motivos de retiro [file:1].
- Problemas de trazabilidad y control, como historización parcial, auditoría incompleta de cambios funcionales y soporte offline-first heterogéneo entre tablas transaccionales [file:1].
- Riesgos para reportería, BI e IA, debido a ausencia de estructuras formales para informes de aprendizaje, falta de horario académico y debilidades en las entidades analíticas y de feature snapshots [file:1].

## 5. Criterio de priorización

El plan está ordenado de adentro hacia afuera para evitar corregir síntomas antes que causas [file:1]. Primero se estabiliza la base estructural del modelo; después se corrige la lógica del dominio académico; luego se atienden rendimiento, crecimiento y mantenibilidad; posteriormente se fortalece la sincronización y trazabilidad; y finalmente se prepara el modelo para reportería, BI e IA [file:1].

Este orden reduce reprocesos porque varias correcciones funcionales dependen de PK, FK, cardinalidades, catálogos y restricciones bien definidos [file:1]. También disminuye el riesgo de migraciones fallidas, ya que evita poblar tablas o construir indicadores sobre relaciones defectuosas o datos no normalizados [file:1].

## 6. Clasificación de tablas

### Paramétricas

Incluyen tablas de referencia relativamente estables como `DocumentType`, `Role`, `Permission`, `AcademicLevel`, `AcademicSublevel`, `PeriodType`, `EnrollmentStatus`, `GradeType`, `EvaluationType`, `ActivityType`, `QualitativeScale`, `PromotionStatus`, `RecoveryProcessType`, `AttendanceStatus`, `AbsenceType`, `IncidentType`, `SocioemotionalSkill`, `UrgencyLevel`, `AlertType`, `RiskFactor`, `SyncStatus`, `SyncOperation` y `SystemConfig` [file:1]. Su función es gobernar reglas del negocio, catálogos operativos y configuraciones del sistema, aunque algunas requieren normalización adicional o redefinición de clave y alcance [file:1].

### Maestras

Corresponden al núcleo persistente del negocio académico: `Person`, `User`, `SchoolYear`, `AcademicGrade`, `Section`, `AcademicPeriod`, `Subject`, `SubjectAcademicConfig` y `Student` [file:1]. Estas tablas deben consolidar identidad, estructura institucional y organización curricular con restricciones claras, baja ambigüedad semántica y trazabilidad temporal suficiente [file:1].

### Transaccionales

Registran eventos u operaciones del sistema: `SubjectOffering`, `TeacherSubjectSection`, `InterdisciplinaryProject`, `Enrollment`, `StudentRepresentative`, `EvaluativeActivity`, `StudentNote`, `ProjectNote`, `RecoveryProcess`, `Attendance`, `ConductIncident`, `DiagnosticEvaluation`, `BehaviorEvaluation`, `SkillEvaluation` y `EarlyAlert` [file:1]. Son las tablas más sensibles para integridad, crecimiento y sincronización, por lo que concentran gran parte de las correcciones de fases 3 a 6 [file:1].

### Puente o intermedias

Resuelven relaciones muchos a muchos o asociaciones compuestas: `RolePermission`, `UserRole`, `SubjectProject` y `StudentRiskFactor` [file:1]. Además, el análisis previo identificó la necesidad de crear nuevas tablas puente para modelar la aplicación de escalas cualitativas y tipos de calificación por subnivel cuando la relación no sea uno a muchos simple [file:1].

### Históricas

`GradeChangeHistory` cumple una función histórica al conservar modificaciones sobre calificaciones [file:1]. También se detectó que el modelo requiere ampliar la historización en procesos académicos y de seguimiento para evitar sobreescritura de información relevante por período o por evento [file:1].

### Auditoría o bitácora

`SyncQueue` cumple función de auditoría técnica de sincronización y colas de procesamiento [file:1]. El análisis también mostró la necesidad de ampliar la bitácora funcional y técnica para cambios sensibles, conflictos de sincronización, recalculaciones y acciones de usuario sobre datos críticos [file:1].

### Analíticas o agregadas

`PeriodGradeSummary`, `StudentRiskScore` y `StudentFeatureSnapshot` operan como entidades agregadas o analíticas para consolidar rendimiento, riesgo y variables derivadas [file:1]. Su diseño es útil para explotación analítica, pero requiere control de versión, gobernanza de recalculación y mejor anclaje al dominio transaccional para evitar inconsistencias [file:1].

### Obsoletas o sin propósito claro

El análisis no identificó tablas completamente prescindibles en bloque, pero sí detectó estructuras con propósito incompleto o definición ambigua, como la autorreferencia de `AcademicPeriod`, la relación inconsistente entre `AcademicSublevel` y `AcademicGrade`, y el diseño actual de `StudentRepresentative` y `SystemConfig` [file:1]. Estas estructuras no deben eliminarse sin revisión de dependencias, pero sí rediseñarse antes de ampliar funcionalidades [file:1].

## 7. Plan por fases

### Fase 0. Preparación

**Objetivo**

Asegurar que la intervención del esquema se ejecute con visibilidad total del estado actual, bajo control de riesgo y con capacidad de reversión [file:1].

**Tareas**

- Generar respaldo completo del esquema y de los datos productivos o de prueba antes de cualquier cambio estructural [file:1].
- Levantar inventario técnico de tablas, índices, constraints, migraciones existentes, vistas, jobs, consultas críticas y dependencias en backend, frontend y procesos ETL, pendiente de validación si no existe repositorio único de migraciones [file:1].
- Validar el esquema real contra el diagrama `models_er.mmd` para detectar diferencias entre documentación y base instalada, especialmente en relaciones declaradas sin campo visible [file:1].
- Identificar dependencias funcionales por módulo, con foco en matrícula, notas, asistencia, conducta, sincronización y reportes [file:1].
- Definir ambiente de remediación, estrategia de migración, pruebas y rollback antes de aplicar cambios sobre tablas transaccionales [file:1].

**Justificación**

Varios hallazgos afectan el corazón relacional del sistema y pueden romper consultas, servicios o procesos de sincronización si se corrigen sin mapa de impacto previo [file:1]. La preparación disminuye el riesgo de pérdida de datos y evita que el equipo corrija el diagrama sin corregir la implementación real [file:1].

**Dependencias**

No depende de fases anteriores; es prerrequisito para todo el plan [file:1].

**Resultado esperado**

Inventario validado, copia de seguridad disponible, diferencias entre modelo lógico y físico documentadas, y plan de ejecución aprobado para las fases siguientes [file:1].

### Fase 1. Corrección estructural

**Objetivo**

Restablecer la consistencia estructural mínima del modelo mediante corrección de PK, FK, cardinalidades, nulabilidad, unicidad y relaciones faltantes o ambiguas [file:1].

**Tareas**

- Eliminar la dependencia circular entre `AcademicSublevel` y `AcademicGrade`, dejando una sola dirección jerárquica consistente [file:1].
- Corregir la relación de `AcademicPeriod` consigo mismo: declarar explícitamente `parent_period` si existe en el esquema físico o eliminar la autorreferencia si fue solo documental [file:1].
- Revisar y corregir relaciones declaradas sin soporte claro en columnas, como la asociación entre `AcademicSublevel` y `GradeType` [file:1].
- Convertir en obligatorias las claves foráneas críticas que hoy aparecen como anulables sin justificación funcional, como `StudentNote.enrollment`, y revisar otros casos equivalentes [file:1].
- Redefinir `SystemConfig` para evitar clave primaria textual como PK operativa y corregir la duplicidad de `updated_at` [file:1].
- Revisar unicidad natural y compuesta en tablas como `Section`, `SubjectAcademicConfig`, `SubjectOffering`, `TeacherSubjectSection`, `Enrollment` y `PeriodGradeSummary`, pendiente de validación en el esquema físico porque el diagrama no detalla índices únicos compuestos [file:1].
- Definir tablas puente explícitas donde una relación potencialmente es muchos a muchos, especialmente para `QualitativeScale` y `GradeType` respecto a `AcademicSublevel` cuando aplique [file:1].

**Justificación**

Sin estructura correcta no es viable estabilizar el dominio académico ni garantizar integridad referencial en datos históricos, operativos o sincronizados [file:1]. Esta fase reduce defectos sistémicos que afectarían todas las migraciones posteriores [file:1].

**Dependencias**

Requiere respaldo, inventario y validación documental de la fase 0 [file:1].

**Resultado esperado**

Esquema con jerarquías claras, relaciones implementables, restricciones mínimas consistentes y base sólida para normalización y ajuste funcional [file:1].

### Fase 2. Normalización y depuración

**Objetivo**

Eliminar atributos ambiguos, redundantes o mal ubicados, y transformar valores libres en estructuras normalizadas que soporten reglas de negocio y análisis consistente [file:1].

**Tareas**

- Sustituir `QualitativeScale.applicable_sublevel` como cadena por una relación normalizada a `AcademicSublevel`, idealmente mediante tabla puente si una escala aplica a varios subniveles [file:1].
- Normalizar `Enrollment.withdrawal_reason` mediante catálogo específico de motivos de retiro [file:1].
- Reemplazar `ConductIncident.severity` entero por un catálogo formal de severidad [file:1].
- Normalizar `DiagnosticEvaluation.socioemotional_area` y `DiagnosticEvaluation.development_level` con tablas paramétricas dedicadas [file:1].
- Revisar `Student.special_needs_type` y otros atributos descriptivos que hoy operan como texto libre para convertirlos en catálogos o dominios controlados, cuando su uso analítico o normativo lo justifique [file:1].
- Depurar relaciones redundantes, como el anclaje simultáneo de `StudentRepresentative` al estudiante y a la matrícula, conservando el nivel semántico correcto [file:1].
- Revisar atributos derivados almacenados en entidades analíticas para documentar su estrategia de recalculación y evitar inconsistencias semánticas [file:1].

**Justificación**

El modelo actual mezcla información nuclear con atributos libres, lo que dificulta validaciones, agregaciones, comparabilidad entre períodos y explotación analítica [file:1]. La normalización reduce ambigüedad y prepara el terreno para reglas académicas más estrictas [file:1].

**Dependencias**

Depende de la fase 1, porque la normalización requiere claves, cardinalidades y relaciones base ya corregidas [file:1].

**Resultado esperado**

Catálogos consistentes, atributos semánticamente controlados, relaciones más limpias y menor riesgo de duplicidad o dependencia transitiva innecesaria [file:1].

### Fase 3. Ajuste del dominio académico

**Objetivo**

Alinear el modelo con la lógica académica real del sistema educativo ecuatoriano, cubriendo matrícula, asistencia, evaluación, conducta, seguimiento, recuperación e informes [file:1].

**Tareas**

- Anclar `EvaluationBlock` a `SubjectOffering` para que la estructura de evaluación exista por asignatura ofertada y no solo por período global [file:1].
- Revisar el flujo completo `EvaluationBlock -> BlockComponent -> ComponentIndicator -> EvaluativeActivity -> StudentNote` para asegurar que cada nota quede vinculada a un contexto académico completo y trazable [file:1].
- Separar o condicionar correctamente la coexistencia de `numeric_score` y `qualitative_scale` en `StudentNote`, de modo que la modalidad de calificación respete nivel, subnivel y tipo de evaluación [file:1].
- Completar el modelado de recuperación académica agregando vínculo explícito con asignatura, plan de refuerzo y seguimiento de sesiones, y validar si `RecoveryProcessType` cubre formalmente mejora y supletorio o si requiere ampliación normativa, pendiente de validación [file:1].
- Incorporar estructura para `LearningReport` o equivalente institucional que consolide calificaciones, asistencia, conducta, observaciones y recomendaciones por período [file:1].
- Incorporar horario académico (`ClassSchedule` o equivalente) para soportar asistencia por bloque de clase, relación docente-hora y análisis de ausentismo por asignatura [file:1].
- Añadir trazabilidad de autoría en `BehaviorEvaluation` y revisar si otras tablas funcionales requieren `created_by`, `evaluated_by` o `approved_by` explícitos [file:1].
- Revisar cobertura de historial académico por período, recuperación, promoción y cambios de estado para garantizar que la evolución del estudiante no se sobrescriba [file:1].
- Validar si la estructura actual cubre integralmente informes de aprendizaje, conducta cualitativa y acompañamiento socioemocional o si se requiere una entidad adicional de seguimiento integral, pendiente de validación [file:1].

**Justificación**

Una vez corregida la base estructural, el siguiente riesgo mayor está en la lógica del negocio académico, donde el modelo todavía no representa de forma completa ni consistente varias reglas esenciales del sistema educativo [file:1]. Esta fase asegura que el esquema deje de ser solo relacionalmente válido y pase a ser académicamente correcto [file:1].

**Dependencias**

Depende de las fases 1 y 2, porque las reglas académicas necesitan relaciones estables, catálogos correctos y semántica normalizada [file:1].

**Resultado esperado**

Modelo académico coherente por período, asignatura, matrícula, subnivel y modalidad de calificación, con soporte más sólido para recuperación, informes y seguimiento integral [file:1].

### Fase 4. Trazabilidad y auditoría

**Objetivo**

Fortalecer la capacidad del sistema para conservar historia, justificar cambios y rastrear acciones funcionales y técnicas sobre datos sensibles [file:1].

**Tareas**

- Extender `GradeChangeHistory` para capturar más contexto de cambio cuando sea necesario, como motivo estandarizado, usuario responsable, origen del cambio y referencias funcionales relacionadas, pendiente de validación de alcance [file:1].
- Definir qué tablas deben historizar cambios en lugar de sobrescribir estado actual, en especial matrícula, recuperación, conducta, seguimiento y configuraciones académicas sensibles [file:1].
- Implementar bitácoras funcionales para cambios críticos en notas finales, promociones, anulaciones, observaciones disciplinarias y cierres de período, pendiente de validación según arquitectura de aplicación [file:1].
- Homogeneizar metadatos de auditoría en tablas transaccionales críticas, incluyendo creación, modificación, usuario responsable, versión y origen del registro cuando aplique [file:1].
- Registrar eventos y conflictos de sincronización de forma más detallada cuando existan actualizaciones concurrentes o reintentos repetidos [file:1].

**Justificación**

La trazabilidad es indispensable para sistemas académicos porque varias decisiones tienen impacto institucional, normativo y familiar [file:1]. También es clave para entornos offline-first, donde la sincronización posterior exige contexto suficiente para resolver conflictos [file:1].

**Dependencias**

Depende de las fases 1 a 3, porque la auditoría debe montarse sobre entidades ya estabilizadas y semánticamente definidas [file:1].

**Resultado esperado**

Modelo con historial funcional suficiente, control de cambios confiable y capacidad de explicar quién hizo qué, cuándo y sobre qué entidad [file:1].

### Fase 5. Escalabilidad y rendimiento

**Objetivo**

Preparar el esquema para crecimiento sostenido de transacciones, consultas operativas intensivas y mantenibilidad a mediano plazo [file:1].

**Tareas**

- Definir índices compuestos en tablas de alto volumen, con prioridad para `Attendance`, `StudentNote`, `Enrollment`, `PeriodGradeSummary`, `EarlyAlert` y tablas de sincronización, pendiente de validación en el motor final [file:1].
- Revisar claves naturales y compuestas de consulta frecuente para evitar búsquedas lineales en operaciones diarias por estudiante, período, asignatura o docente [file:1].
- Establecer política de partición lógica o archivado por año lectivo en tablas transaccionales de crecimiento rápido, pendiente de validación según motor y volumen esperado [file:1].
- Reducir joins innecesarios introducidos por relaciones mal ancladas, especialmente en evaluación, recuperación y asistencia [file:1].
- Documentar estrategia de mantenimiento de entidades analíticas para evitar recalcular masivamente métricas en cada consulta operativa [file:1].

**Justificación**

Asistencia, notas, alertas y snapshots crecerán rápido y pueden volverse cuellos de botella si no se optimiza el acceso desde el modelo [file:1]. Mejorar rendimiento en esta etapa evita que la deuda estructural reaparezca como deuda operativa [file:1].

**Dependencias**

Depende de las fases 1 a 4, ya que no conviene indexar de forma definitiva tablas o relaciones que todavía podrían cambiar [file:1].

**Resultado esperado**

Esquema más estable bajo carga, consultas críticas más eficientes y menor costo de mantenimiento conforme aumente el volumen de datos [file:1].

### Fase 6. Offline-first y sincronización

**Objetivo**

Consolidar una estrategia consistente de sincronización diferida, control de conflictos y trazabilidad entre entornos locales y remotos [file:1].

**Tareas**

- Estandarizar columnas de sincronización en todas las tablas transaccionales que deban operar offline, evitando que unas tengan `uuid`, `sync_status`, `sync_version`, `device_origin` y otras no [file:1].
- Revisar el rol de `SyncQueue`, `SyncStatus` y `SyncOperation` para garantizar que la cola soporte reintentos, errores, idempotencia y auditoría técnica suficiente [file:1].
- Añadir versionado de esquema de `payload` o contrato de sincronización para evitar incompatibilidades silenciosas entre versiones de cliente y servidor [file:1].
- Definir reglas de resolución de conflictos por entidad, incluyendo precedencia temporal, bloqueo lógico, conciliación manual o fusión controlada, pendiente de validación de arquitectura [file:1].
- Establecer criterios de sincronización para calificaciones, asistencia, conducta y alertas, donde los conflictos tienen alto impacto funcional [file:1].

**Justificación**

El modelo ya incorpora elementos offline-first, pero lo hace de forma desigual y con riesgos de consistencia entre módulos [file:1]. Esta fase busca convertir un soporte parcial en una arquitectura sincronizable de forma controlada [file:1].

**Dependencias**

Depende de las fases 1 a 5, porque la sincronización robusta requiere entidades bien definidas, claves estables, auditoría y rendimiento adecuado [file:1].

**Resultado esperado**

Modelo listo para operación híbrida local/remota, con menor probabilidad de duplicidad, pérdida de cambios o conflictos opacos [file:1].

### Fase 7. Reportería, BI e IA

**Objetivo**

Preparar la base para explotación analítica, reportería institucional y futura construcción de módulos de inteligencia predictiva [file:1].

**Tareas**

- Formalizar `LearningReport` y vistas de consolidación académica por estudiante, período, asignatura y sección [file:1].
- Revisar `StudentFeatureSnapshot` para agregar control de vigencia, versión y estrategia de recalculación reproducible [file:1].
- Asegurar que las variables clave de riesgo académico estén ancladas a datos transaccionales consistentes y no a textos libres o relaciones ambiguas [file:1].
- Definir datasets derivados y vistas analíticas para asistencia, rendimiento, conducta, alertas y trayectorias académicas, pendiente de validación según stack analítico [file:1].
- Incorporar las variables faltantes de contexto estudiantil cuando estén justificadas y normativamente permitidas para mejorar la capacidad predictiva [file:1].
- Alinear nombres, códigos y catálogos para que indicadores, cubos o pipelines de ML no dependan de limpieza manual posterior [file:1].

**Justificación**

La analítica solo es confiable si opera sobre un modelo transaccional sano, trazable y semánticamente estable [file:1]. Ejecutar esta fase demasiado pronto produciría indicadores frágiles y modelos sesgados por defectos del esquema [file:1].

**Dependencias**

Depende de las fases 1 a 6, porque reportería, BI e IA consumen todas las capas previas del modelo [file:1].

**Resultado esperado**

Base de datos preparada para reportes institucionales confiables, datasets consistentes y evolución hacia analítica avanzada y predicción temprana [file:1].

### Fase 8. Validación final

**Objetivo**

Verificar que el rediseño implementado cumple integridad, funcionalidad, rendimiento y trazabilidad antes de cierre técnico [file:1].

**Tareas**

- Ejecutar pruebas de integridad referencial, nulabilidad, unicidad y restricciones de negocio sobre el nuevo esquema [file:1].
- Probar flujos funcionales completos de matrícula, asistencia, evaluación, recuperación, conducta, alertas y sincronización [file:1].
- Validar la migración de datos históricos y confirmar que no existan huérfanos, duplicados semánticos ni pérdidas de trazabilidad [file:1].
- Confirmar que el nuevo modelo soporta los reportes académicos e insumos analíticos previstos por el sistema [file:1].
- Aplicar checklist de cierre con revisión conjunta entre arquitectura, desarrollo, QA y negocio, pendiente de validación organizacional [file:1].

**Justificación**

Sin validación final, una corrección técnicamente bien diseñada puede fallar en operación real o romper procesos académicos de alta criticidad [file:1]. Esta fase asegura cierre formal y reduce la probabilidad de deuda post-migración [file:1].

**Dependencias**

Depende de la ejecución controlada de todas las fases anteriores [file:1].

**Resultado esperado**

Modelo corregido, validado, documentado y listo para adopción operativa o evolución incremental [file:1].

## 8. Tareas por prioridad

### Prioridad alta

- Corregir la jerarquía `AcademicLevel -> AcademicSublevel -> AcademicGrade -> Section` eliminando dependencias circulares o ambiguas [file:1].
- Resolver relaciones declaradas sin soporte claro en columnas, especialmente en `AcademicPeriod` y `GradeType` [file:1].
- Reforzar FK y nulabilidad en tablas críticas como `StudentNote` y revisar constraints equivalentes [file:1].
- Anclar `EvaluationBlock` a `SubjectOffering` y corregir la trazabilidad completa de evaluación por asignatura [file:1].
- Normalizar catálogos libres de alto impacto: subnivel aplicable, motivos de retiro, severidad de incidentes y componentes de evaluación diagnóstica [file:1].
- Rediseñar `StudentRepresentative` para eliminar ambigüedad entre estudiante y matrícula [file:1].
- Definir estructura formal para informes de aprendizaje y horario académico [file:1].

### Prioridad media

- Completar el modelado de recuperación, mejora y validación de supletorio dentro de la estructura académica [file:1].
- Extender trazabilidad funcional y técnica en notas, conducta, configuraciones y sincronización [file:1].
- Revisar `SystemConfig` y otros catálogos con problemas de diseño o claves poco robustas [file:1].
- Incorporar índices compuestos y estrategia de crecimiento de tablas transaccionales [file:1].
- Homogeneizar metadatos offline-first entre tablas operativas [file:1].

### Prioridad baja

- Optimizar entidades analíticas y materializaciones para reportería avanzada [file:1].
- Ampliar variables de contexto estudiantil para modelos predictivos, sujetas a validación normativa y disponibilidad operativa [file:1].
- Establecer datasets especializados, vistas de BI y contratos estables para consumo analítico [file:1].

## 9. Dependencias entre tareas

La corrección de cardinalidades, PK y FK debe ejecutarse antes de cualquier normalización avanzada, porque los catálogos y tablas puente dependen de relaciones base correctamente definidas [file:1]. La normalización debe completarse antes del ajuste académico, ya que reglas como modalidad de calificación, recuperación o clasificación de incidentes requieren dominios y referencias confiables [file:1].

El ajuste del dominio académico debe preceder a la trazabilidad ampliada, porque no conviene historizar estructuras funcionales todavía inestables [file:1]. La optimización de rendimiento debe llegar después del rediseño funcional principal para evitar índices o planes de acceso sobre tablas que aún cambian [file:1]. El fortalecimiento offline-first debe apoyarse en claves estables, auditoría y contratos definidos, mientras que reportería, BI e IA solo deben implementarse sobre un modelo ya consistente y validado [file:1].

## 10. Riesgos de no corregir

No ejecutar este plan mantiene defectos que pueden provocar inconsistencia referencial, imposibilidad de representar correctamente procesos académicos y generación de datos ambiguos o inválidos [file:1]. En operación, esto se traduce en notas mal contextualizadas, asistencia difícil de analizar por asignatura, recuperación académica incompleta y reportes institucionales con menor confiabilidad [file:1].

También persiste el riesgo de degradación de rendimiento a medida que crecen las tablas transaccionales sin índices adecuados ni anclajes correctos [file:1]. En escenarios offline-first, las inconsistencias de sincronización y la falta de versionado homogéneo pueden amplificar duplicados, conflictos y pérdidas de trazabilidad [file:1]. Finalmente, cualquier módulo de reportería, BI o IA construido sobre el modelo actual heredará sesgos, vacíos estructurales y debilidad semántica desde la capa transaccional [file:1].

## 11. Resultado esperado

Al finalizar todas las fases, la base de datos debe quedar estructuralmente consistente, académicamente alineada, normalizada en sus catálogos críticos y preparada para operación transaccional confiable [file:1]. El modelo debe representar correctamente período, asignatura, matrícula, evaluación, conducta, seguimiento e historia académica sin ambigüedades de cardinalidad ni dependencias circulares [file:1].

Además, debe quedar lista para escalamiento, sincronización offline-first controlada, reportería institucional reproducible y evolución hacia analítica e inteligencia artificial con datos mejor gobernados [file:1]. El resultado esperado no es solo un esquema corregido, sino una plataforma de datos sostenible para crecimiento funcional futuro [file:1].

---

## A. Checklist ejecutivo

- [ ] Generar respaldo completo y validar el esquema real contra el diagrama actual [file:1].
- [ ] Eliminar dependencia circular entre `AcademicSublevel` y `AcademicGrade` [file:1].
- [ ] Corregir la relación autorreferente de `AcademicPeriod` y las relaciones declaradas sin columna explícita [file:1].
- [ ] Hacer obligatorias las FK críticas anulables sin justificación, empezando por `StudentNote.enrollment` [file:1].
- [ ] Normalizar catálogos libres clave: subnivel aplicable, motivo de retiro, severidad e insumos diagnósticos [file:1].
- [ ] Vincular `EvaluationBlock` con `SubjectOffering` [file:1].
- [ ] Rediseñar `StudentRepresentative` y completar la estructura de recuperación académica [file:1].
- [ ] Crear estructura de horario académico y de informe de aprendizaje [file:1].
- [ ] Estandarizar auditoría y sincronización offline-first [file:1].
- [ ] Validar integridad, funcionalidad y rendimiento del modelo rediseñado [file:1].

## B. Orden ideal de ejecución

1. Respaldo, inventario y validación del esquema actual [file:1].
2. Corrección de PK, FK, cardinalidades y nulabilidad [file:1].
3. Normalización de catálogos y eliminación de ambigüedades semánticas [file:1].
4. Ajuste de la lógica académica por asignatura, período y modalidad de evaluación [file:1].
5. Incorporación de historización, auditoría y control de cambios [file:1].
6. Optimización de índices, crecimiento y mantenibilidad [file:1].
7. Homologación del modelo offline-first y sincronización [file:1].
8. Habilitación de reportería, BI e IA sobre la base corregida [file:1].
9. Validación integral y cierre técnico [file:1].

## C. Quick wins

- Corregir la duplicidad de `updated_at` en `SystemConfig` y revisar su clave primaria [file:1].
- Convertir `withdrawal_reason`, `severity` y campos diagnósticos libres en catálogos o FKs [file:1].
- Hacer `StudentNote.enrollment` no nulo si no existe un caso funcional documentado para dejarlo abierto [file:1].
- Añadir índices compuestos básicos en asistencia y notas, una vez fijadas las relaciones definitivas [file:1].
- Agregar autoría explícita en `BehaviorEvaluation` [file:1].

## D. Cambios de alto riesgo

- Eliminación de la dependencia circular entre `AcademicSublevel` y `AcademicGrade`, porque puede afectar migraciones, cargas iniciales y consultas existentes [file:1].
- Rediseño del flujo de evaluación desde `EvaluationBlock` hasta `StudentNote`, porque impacta lógica académica, UI, reportes y cálculo de promedios [file:1].
- Normalización de `StudentRepresentative`, porque puede requerir migración de datos históricos con diferente granularidad temporal [file:1].
- Incorporación de `LearningReport` y `ClassSchedule`, porque introduce nuevas dependencias funcionales y consultas transversales [file:1].
- Homologación offline-first y de sincronización, porque cualquier cambio en identificadores, versionado o payload puede romper compatibilidad entre clientes y servidor [file:1].
