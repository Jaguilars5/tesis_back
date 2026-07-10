# Sistema de Gestión Académica - Backend

Este repositorio contiene la lógica del lado del servidor para el sistema de gestión académica institucional. Desarrollado con Django y Django REST Framework, el sistema proporciona una infraestructura robusta para la administración de procesos escolares, seguimiento de estudiantes y análisis de riesgo académico.

## Arquitectura del Sistema

El proyecto implementa una arquitectura modular y desacoplada que separa las responsabilidades en cuatro capas principales: Modelos, Repositorios, Servicios y API. Esta estructura permite un mantenimiento independiente de la lógica de negocio frente a la infraestructura de datos o la interfaz de comunicación.

Para una descripción detallada de la organización del código y los patrones de diseño aplicados, consulte la [Documentación de Arquitectura](docs/STRUCTURE.md).

## Módulos del Proyecto

El sistema está organizado en los siguientes módulos funcionales:

### Gestión de Identidad y Acceso (IAM & Core)

Administración de usuarios, roles y permisos. El login es por **username** (autogenerado: primera letra del nombre + primer apellido + numeración si existe duplicado). El módulo `core` proporciona las utilidades transversales y estándares de respuesta para todo el sistema.
[Documentación de IAM](apps/iam/README.md) | [Documentación de Core](apps/core/README.md)

### Institución y Estructura Académica (Institutions & Academic)

Definición de la infraestructura institucional (sedes, aulas) y la estructura curricular (años lectivos, secciones, materias y mallas curriculares).
[Documentación de Institutions](apps/institutions/README.md) | [Documentación de Academic](apps/academic/README.md)

### Registro y Expediente Estudiantil (Students)

Gestión integral de la información del estudiante, incluyendo su historial de matrícula y la relación con sus representantes legales y contactos de emergencia.
[Documentación del Módulo Students](apps/students/README.md)

### Calificaciones y Seguimiento Diario (Grading)

Módulo encargado del registro de calificaciones estructurado en bloques de evaluación. Gestiona tipos de calificación, escalas cualitativas y procesos de recuperación académica.
[Documentación del Módulo Grading](apps/grading/README.md)

### Asistencia y Comportamiento (Attendance)

Gestión de asistencia diaria, incidentes conductuales, evaluaciones socioemocionales y cálculo de promedios de comportamiento. Sincroniza datos para operaciones en entornos con conectividad limitada.
[Documentación del Módulo Attendance](apps/attendance/README.md)

### Analítica y Riesgo Académico (Analytics)

Análisis de riesgo estudiantil basado en métricas de asistencia, rendimiento académico y conducta. Genera perfiles de riesgo y prioriza estudiantes que requieren intervención. Incluye un modelo de Machine Learning (regresión logística) para predicción de riesgo académico.

```bash
# Sembrar configuración de scoring (ejecutar una vez antes de entrenar)
python manage.py seed_scoring_config

# Entrenar modelo de riesgo (usa todos los StudentFeatureSnapshot históricos)
python manage.py train_risk_model

# Sincronizar etiquetas de riesgo post-entrenamiento
python manage.py sync_risk_labels
```

**Scripts de análisis y diagnóstico:**
```bash
python scripts/analyze_historical_data.py   # Diagnóstico de cobertura de datos
python scripts/inspect_risk_scores.py        # Inspeccionar scores generados
python scripts/debug_predict.py              # Probar predicción con datos de ejemplo
```

> **Nota**: Si el modelo entrenado no existe, el sistema usa reglas heurísticas como fallback. El artefacto entrenado se guarda en `apps/analytics/ml/risk_model.joblib`.

### Configuración del Sistema (Configuration)

Gestión de parámetros configurables del sistema, incluyendo periodos académicos, tipos de evaluación y catálogos generales.

### Integración con Terceros (Integration)

Endpoints y servicios para integración con sistemas externos y sincronización de datos.

---

> **Nota**: El proyecto cuenta con 12 apps en total (`core`, `iam`, `people`, `institutions`, `students`, `academic`, `grading`, `attendance`, `behavior`, `analytics`, `configuration`, `integration`). Consulte la [Documentación de Arquitectura](docs/STRUCTURE.md) para más detalles.

## Diagrama de Base de Datos

El diseño de la base de datos se basa en un modelo relacional normalizado que asegura la integridad de la información académica. Las relaciones clave incluyen la vinculación entre periodos académicos, actividades de evaluación y registros de estudiantes.

El esquema detallado de las entidades y sus relaciones puede visualizarse en el archivo de documentación técnica [Diagrama ER](docs/bd_en.html).

## Seeds (Datos Iniciales)

Los siguientes comandos son idempotentes y deben ejecutarse en orden después de las migraciones para poblar los catálogos, permisos y datos de prueba:

```bash
# 1. Catálogos del sistema (tipos de documento, etc.)
python manage.py seed_catalogs

# 2. Permisos + Roles (DOCENTE, ESTUDIANTE, etc.)
python manage.py seed_permissions

# 3. Configuración de scoring de riesgo
python manage.py seed_scoring_config

# 4. Datos de prueba
python manage.py seed_test_data
```

## Pruebas Automatizadas

El proyecto cuenta con una suite de 569+ pruebas que cubre modelos, servicios y API de todos los módulos.

```bash
# Ejecutar todas las pruebas (usa SQLite, no requiere PostgreSQL)
python manage.py test --settings=config.settings.test

# Ejecutar pruebas de un módulo específico
python manage.py test apps.iam --settings=config.settings.test
python manage.py test apps.grading.tests.test_models --settings=config.settings.test

# Pruebas de seguridad
python manage.py test apps.core.tests --settings=config.settings.test

# Con coverage
coverage run --source='.' manage.py test --settings=config.settings.test
coverage report -m
```

## Estándares de Comunicación (API)

Para garantizar la consistencia entre el Backend y el Frontend, todas las respuestas siguen un formato estandarizado procesado por el módulo `apps.core`:

```json
{
    "ok": true,       // Indica si la operación fue exitosa
    "data": { ... },  // Contiene los datos solicitados o detalles del error
    "msg": ""         // Mensaje descriptivo opcional
}
```

- **Paginación**: Los listados grandes incluyen metadatos de navegación dentro del objeto `data`.
- **Errores**: Las excepciones son capturadas globalmente para devolver siempre el formato JSON anterior con el código HTTP correspondiente.

## Infraestructura y Tecnologías

- **Backend**: Django 4.2.x.
- **API**: Django REST Framework, con filtros y paginación personalizados.
- **Autenticación**: JWT con `djangorestframework-simplejwt` y modelo de usuario extendido. Login por **username** con generación automática.
- **CORS**: `django-cors-headers` para integración con frontends separados.
- **Consultas y filtros**: `django-filter` para búsqueda y filtrado de endpoints.
- **Tareas asíncronas**: Celery como worker y Redis como broker.
- **Caché**: `django-redis` para cache distribuida y soporte de Redis.
- **Base de datos**: PostgreSQL (desarrollo y producción).
- **Contenedores**: Docker y Docker Compose para aislar web, base de datos, Redis, Celery y Flower.
- **Configuración**: Estructura modular (`base`, `local`, `production`) y variables de entorno desde `.env`.
- **Servidor WSGI**: Gunicorn como opción de despliegue.
- **Utilidades**: `python-dotenv` para cargar variables, `psycopg2-binary` para PostgreSQL y `bcrypt` para hash de contraseñas.

Consulte la [Guía de Usuario y Manual Técnico](docs/USER_GUIDE.md) para más información.

## Requisitos e Instalación

### Opción 1: Desarrollo con Docker (Recomendado)

La forma más sencilla de configurar el entorno es usando Docker, que aísla todas las dependencias:

```bash
# 1. Clonar el repositorio
git clone https://github.com/Jaguilars5/tesis_back.git
cd tesis_back

# 2. Construir la imagen Docker
docker-compose build

# 3. Iniciar los servicios
docker-compose up

# 4. En otra terminal: poblar datos iniciales
docker-compose exec web python manage.py seed_catalogs
docker-compose exec web python manage.py seed_permissions
docker-compose exec web python manage.py seed_scoring_config
docker-compose exec web python manage.py seed_test_data

# 5. Crear superusuario
docker-compose exec web python manage.py createsuperuser

# 6. Acceder a la aplicación
# API: http://localhost:8000
# Admin: http://localhost:8000/admin
# Flower (Celery monitor): http://localhost:5555

# API Docs (Swagger): http://localhost:8000/api/docs/
# API Docs (ReDoc): http://localhost:8000/api/redoc/
```

**Para verificar que todo está configurado correctamente:**

```bash
bash scripts/verify_docker_setup.sh
```

**Documentación completa de Docker:**
Consulta [docs/DOCKER.md](docs/DOCKER.md) para instrucciones detalladas, troubleshooting y mejores prácticas.

### Opción 2: Instalación Local (Sin Docker)

Si prefieres desarrollo local sin Docker:

**Requisitos Previos:**

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Entorno virtual (venv)

**Pasos:**

```bash
# 1. Clonar el repositorio
git clone https://github.com/Jaguilars5/tesis_back.git
cd tesis_back

# 2. Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores locales (DB_HOST=localhost, etc.)

# 5. Ejecutar migraciones
python manage.py migrate

# 6. Poblar datos iniciales (idempotente, ejecutar en orden)
python manage.py seed_catalogs
python manage.py seed_permissions
python manage.py seed_scoring_config
python manage.py seed_test_data

# 7. Crear superusuario
python manage.py createsuperuser

# 8. Iniciar servidor de desarrollo
python manage.py runserver

# 9. En otra terminal: iniciar Celery
celery -A config worker --loglevel=info

# 10. Opcional: iniciar Flower
celery -A config flower --port=5555
```
