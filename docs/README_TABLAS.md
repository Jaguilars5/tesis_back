# Guía Simplificada de la Base de Datos: SIGAE (Sistema de Gestión Académica)

Esta guía explica de forma sencilla y directa el propósito de cada una de las 48 tablas de la base de datos de **SIGAE v3**. Está estructurada por módulos lógicos, ideal para servir como material de apoyo en presentaciones, diapositivas o sesiones de alineación técnica.

---

## Índice de Módulos
1. [Estructura Académica (El Esqueleto)](#1-estructura-académica-el-esqueleto)
2. [Personas, Vínculos y Seguridad (Los Actores)](#2-personas-vínculos-y-seguridad-los-actores)
3. [Matrículas (El Registro)](#3-matrículas-el-registro)
4. [Evaluaciones e Instrumentos (Las Calificaciones)](#4-evaluaciones-e-instrumentos-las-calificaciones)
5. [Asistencia y Conducta (El Día a Día)](#5-asistencia-y-conducta-el-día-a-día)
6. [Analítica Predictiva e IA (La Alerta Temprana)](#6-analítica-predictiva-e-ia-la-alerta-temprana)
7. [Catálogos Paramétricos (Las Opciones del Sistema)](#7-catálogos-paramétricos-las-opciones-del-sistema)
8. [Configuración, Auditoría y Sincronización (El Soporte Técnico)](#8-configuración-auditoría-y-sincronización-el-soporte-técnico)

---

## 1. Estructura Académica (El Esqueleto)
Define cómo se organiza la institución educativa en términos de tiempo, niveles curriculares y materias.

*   **`ANNO_ESCOLAR`**: Controla los períodos lectivos anuales (ej. *2025-2026*). Define cuándo inicia y termina un año escolar y cuál está activo.
*   **`NIVEL_ACADEMICO`**: Clasifica las etapas de la educación (ej. *Educación General Básica, Bachillerato*).
*   **`GRADO_ACADEMICO`**: Los años o cursos específicos dentro de un nivel (ej. *8.º de Básica, 3.º de Bachillerato*). Determina las reglas de evaluación de ese grupo.
*   **`SECCION`** (o `PARALELO`): Representa un curso físico o aula (ej. *8.º de Básica paralelo "A"*). Define la capacidad de alumnos para ese grupo en un año lectivo.
*   **`ASIGNATURA`**: El catálogo general de materias disponibles en el currículo (ej. *Matemática, Lengua y Literatura*).
*   **`CONFIGURACION_ASIGNATURA`**: Personaliza las materias para cada grado (ej. *Matemática en 8.º de Básica tiene 5 horas semanales y es obligatoria*).
*   **`OFERTA_ASIGNATURA`**: La asignatura en acción. Cruza una asignatura configurada con una sección específica en el año lectivo en curso (ej. *Matemática ofertada para 8.º "A" en 2025-2026*).
*   **`PERIODO_ACADEMICO`**: Divide el año escolar en lapsos de tiempo para evaluar (ej. *Primer Trimestre, Supletorio*).

---

## 2. Personas, Vínculos y Seguridad (Los Actores)
Registra a toda la comunidad educativa y administra qué puede hacer cada usuario en el sistema.

*   **`PERSONA`**: Información civil básica de cualquier individuo en el sistema (nombres, cédula, correo, teléfono). Evita duplicidad de datos si alguien es docente y representante a la vez.
*   **`USUARIO`**: Habilita el inicio de sesión y credenciales de acceso vinculando a una `PERSONA` (almacena el hash de contraseña y tipo de usuario).
*   **`PERFIL_ESTUDIANTE`**: Datos específicos y críticos del estudiante (código estudiantil, NEE - Necesidades Educativas Especiales, distancia al colegio, zona de residencia).
*   **`VINCULO_FAMILIAR`**: Asocia a un estudiante con su representante legal o parientes, indicando si está autorizado para retirarlo o si recibe notificaciones.
*   **`ASIGNACION_DOCENTE`**: Vincula a un docente (`USUARIO`) con la materia específica que dicta en un curso (`OFERTA_ASIGNATURA`).
*   **`ROL`**: Perfiles de acceso generales (ej. *Docente, Director, DECE*).
*   **`PERMISO`**: Acciones atómicas permitidas en el sistema (ej. *crear notas, registrar asistencia*).
*   **`USUARIO_ROL`**: Asigna roles temporales o permanentes a los usuarios.
*   **`ROL_PERMISO`**: Configura qué permisos atómicos componen cada rol.

---

## 3. Matrículas (El Registro)
*   **`MATRICULA`**: Representa el "contrato académico" del alumno. Vincula el perfil del estudiante con una sección y un año escolar. Registra si es repitente, cuándo se matriculó y, de ser el caso, cuándo y por qué se retiró de la institución.

---

## 4. Evaluaciones e Instrumentos (Las Calificaciones)
Estructura cómo se califica a los estudiantes, desde proyectos interdisciplinares hasta tareas diarias y recuperaciones.

*   **`BLOQUE_EVALUACION`**: Define los componentes de la nota de un trimestre (ej. *Evaluación Formativa - 70%, Evaluación Sumativa - 30%*).
*   **`COMPONENTE_BLOQUE`**: Subdivisiones de un bloque (ej. *Lecciones Orales, Tareas, Talleres grupales*).
*   **`INDICADOR_COMPONENTE`**: El aprendizaje específico que se está midiendo (ej. *Resuelve ecuaciones lineales*).
*   **`ACTIVIDAD_EVALUATIVA`**: Las tareas físicas, talleres o exámenes creados por el docente para calificar un indicador (ej. *Tarea 1: Ecuaciones de 1er Grado*).
*   **`NOTA_ACTIVIDAD`**: La calificación numérica (del 1 al 10) obtenida por un estudiante en una actividad específica. Soporta auditoría y sincronización offline.
*   **`PROYECTO_INTERDISCIPLINAR`**: Proyectos prácticos que evalúan múltiples asignaturas juntas en un período (ej. *Estadística Ambiental*).
*   **`PROYECTO_ASIGNATURA`**: Declara qué asignaturas y ofertas participan en un proyecto interdisciplinar.
*   **`NOTA_PROYECTO`**: Calificación final del proyecto de un alumno, dividida en nota de producto y nota de exposición oral.
*   **`EVALUACION_DIAGNOSTICA`**: Diagnóstico socioemocional y psicológico que realiza el DECE o los docentes al inicio del período escolar para detectar necesidades de apoyo.
*   **`PROCESO_RECUPERACION`**: Registra los procesos de mejora pedagógica o exámenes supletorios para estudiantes con bajas notas, calculando su promedio final corregido.
*   **`RESUMEN_CALIFICACION_PERIODO`**: Consolida los promedios formativos y sumativos de un estudiante en una materia al finalizar un período, indicando si aprueba o requiere recuperación.

---

## 5. Asistencia y Conducta (El Día a Día)
Monitorea la permanencia de los estudiantes en las aulas y su comportamiento en la convivencia escolar.

*   **`REGISTRO_ASISTENCIA`**: Registro diario por materia de la asistencia de cada estudiante (Presente, Retraso, Falta Justificada o Injustificada).
*   **`INCIDENTE_DISCIPLINARIO`**: Bitácora de faltas de convivencia (severidad, descripción de lo ocurrido, acciones tomadas y si se notificó a la familia).
*   **`EVALUACION_HABILIDAD`**: Evaluaciones cualitativas periódicas sobre habilidades socioemocionales priorizadas (ej. *Empatía y respeto*).
*   **`RESUMEN_COMPORTAMIENTO_PERIODO`**: Calificación cualitativa consolidada (A, B, C, D, E) del comportamiento del estudiante en un período.

---

## 6. Analítica Predictiva e IA (La Alerta Temprana)
El módulo inteligente diseñado para identificar tempranamente el riesgo de deserción escolar.

*   **`SNAPSHOT_FEATURES_ML`**: Una "foto" histórica del comportamiento del estudiante (asistencias, incidentes, tendencia de notas, NEE, distancia al colegio). Sirve como el set de datos de entrada para los modelos de Machine Learning.
*   **`PREDICCION_DESERCION`**: Almacena el resultado del modelo de IA: la probabilidad numérica de riesgo de deserción y su etiqueta (Bajo, Medio, Alto, Crítico) para cada estudiante en un período.
*   **`DETALLE_FACTOR_PREDICCION`**: Explica el "porqué" de la predicción de IA (SHAP values), indicando cuáles fueron los factores más influyentes (ej. *Faltas consecutivas aportó un 30% al riesgo*).
*   **`ALERTA_TEMPRANA`**: Alertas generadas por el sistema al cruzar la IA o reglas duras (ej. *Alerta Roja por 5 faltas injustificadas*). Rastrea quién atendió la alerta y qué acciones se tomaron.

---

## 7. Catálogos Paramétricos (Las Opciones del Sistema)
Tablas maestras que definen opciones fijas para homogeneizar la información y evitar errores de escritura manual.

*   **`TIPO_DOCUMENTO`**: Catálogo de identificaciones válidas (Cédula, Pasaporte, etc.).
*   **`TIPO_CALIFICACION`**: Clasificación de notas (Formativa, Sumativa, Diagnóstica).
*   **`ESTADO_ASISTENCIA`**: Opciones de asistencia (Presente, Ausente, Retraso).
*   **`ESTADO_MATRICULA`**: Fases de la matrícula (Registrada, Activa, Retirada, Anulada).
*   **`FACTOR_RIESGO`**: Factores de riesgo de deserción predefinidos para la IA (ej. *Bajo Rendimiento, Absentismo, Trabajo Infantil*).
*   **`ESCALA_CUALITATIVA`**: Equivalencias cualitativas del Ministerio de Educación (ej. *Domina los aprendizajes requeridos, Próximo a alcanzar*).
*   **`TIPO_INCIDENTE`**: Tipos de faltas disciplinarias (Falta Leve, Acoso Escolar, Daño material).
*   **`HABILIDAD_SOCIOEMOCIONAL`**: Catálogo de habilidades blandas a observar (Empatía, Autoreregulación, Resolución de conflictos).

---

## 8. Configuración, Auditoría y Sincronización (El Soporte Técnico)
Garantiza el correcto funcionamiento técnico, la seguridad de los datos y el trabajo sin conexión.

*   **`CONFIG_SISTEMA`**: Variables de configuración global (ej. *el porcentaje formativo por defecto es 70%*).
*   **`AUDITORIA_NOTA`**: Bitácora de seguridad estricta. Si un docente cambia una calificación ya registrada, almacena el valor previo, el nuevo valor, la justificación y quién realizó el cambio.
*   **`COLA_SINCRONIZACION`**: Administra el funcionamiento offline de la aplicación móvil. Si un docente registra notas o asistencias en el campo sin internet, esta tabla almacena los cambios en cola y los sincroniza ordenadamente cuando se recupera la conexión.
