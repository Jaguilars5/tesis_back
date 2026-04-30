# Sistema de Gestión Académica - Backend

Este repositorio contiene la lógica del lado del servidor para el sistema de gestión académica institucional. Desarrollado con Django y Django REST Framework, el sistema proporciona una infraestructura robusta para la administración de procesos escolares, seguimiento de estudiantes y análisis de riesgo académico.

## Arquitectura del Sistema

El proyecto implementa una arquitectura modular y desacoplada que separa las responsabilidades en cuatro capas principales: Modelos, Repositorios, Servicios y API. Esta estructura permite un mantenimiento independiente de la lógica de negocio frente a la infraestructura de datos o la interfaz de comunicación.

Para una descripción detallada de la organización del código y los patrones de diseño aplicados, consulte la [Documentación de Arquitectura](docs/STRUCTURE.md).

## Módulos del Proyecto

El sistema está organizado en los siguientes módulos funcionales:

### Gestión de Identidad y Acceso (Accounts & Core)
Administración de usuarios, roles y permisos. El módulo `core` proporciona las utilidades transversales y estándares de respuesta para todo el sistema.
[Documentación de Accounts](apps/accounts/README.md) | [Documentación de Core](apps/core/README.md)

### Institución y Estructura Académica (Institutions & Academic)
Definición de la infraestructura institucional (sedes, aulas) y la estructura curricular (años lectivos, secciones, materias y mallas curriculares).
[Documentación de Institutions](apps/institutions/README.md) | [Documentación de Academic](apps/academic/README.md)

### Registro y Expediente Estudiantil (Students)
Gestión integral de la información del estudiante, incluyendo su historial de matrícula y la relación con sus representantes legales y contactos de emergencia.
[Documentación del Módulo Students](apps/students/README.md)

### Calificaciones y Seguimiento Diario (Grading)
Módulo encargado del registro de notas, control de asistencia y bitácora de incidentes conductuales. Soporta la sincronización de datos para operaciones en entornos con conectividad limitada.
[Documentación del Módulo Grading](apps/grading/README.md)

### Planificación y Horarios (Scheduling)
Gestión de la disponibilidad docente y generación de horarios de clase, optimizando el uso de recursos físicos y temporales.
[Documentación del Módulo Scheduling](apps/scheduling/README.md)

## Diagrama de Base de Datos

El diseño de la base de datos se basa en un modelo relacional normalizado que asegura la integridad de la información académica. Las relaciones clave incluyen la vinculación entre periodos académicos, actividades de evaluación y registros de estudiantes.

El esquema detallado de las entidades y sus relaciones puede visualizarse en el archivo de documentación técnica [Diagrama ER](bd.html).

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

- **Framework**: Django 6.0+ & Django REST Framework.
- **Autenticación**: JWT (SimpleJWT) con modelo de usuario extendido.
- **Tareas Asíncronas**: Celery + Redis para procesos pesados.
- **Base de Datos**: PostgreSQL / SQL Server (Production).
- **Configuración**: Modular (Base, Local, Production) con variables de entorno `.env`.

Consulte la [Guía de Usuario y Manual Técnico](docs/USER_GUIDE.md) para más información.

## Requisitos e Instalación

### Requisitos Previos
- Python 3.10+
- Entorno virtual configurado (venv)
- Dependencias listadas en el entorno (PyJWT, bcrypt, python-dotenv, mssql-django)

### Pasos de Instalación
1. Clonar el repositorio.
2. Configurar las variables de entorno en un archivo `.env` basado en la plantilla de configuración.
3. Instalar las dependencias: `pip install -r requirements.txt` (o instalación manual de paquetes requeridos).
4. Ejecutar las migraciones: `python manage.py migrate`.
5. Iniciar el servidor de desarrollo: `python manage.py runserver`.
