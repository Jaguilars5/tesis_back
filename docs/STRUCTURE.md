# Arquitectura y Estructura del Proyecto

Este documento describe la arquitectura técnica y la organización de archivos del backend del sistema de gestión académica.

## Arquitectura del Proyecto

El sistema sigue una arquitectura orientada a servicios y dominios, diseñada para ser escalable, mantenible y desacoplada. Se utiliza Django como framework base, pero con una organización que separa claramente las responsabilidades.

### Capas de la Aplicación

Cada módulo (app) del sistema se divide en las siguientes capas funcionales:

1.  **Capa de Modelos (Models)**: Define el esquema de la base de datos utilizando el ORM de Django. Incluye validaciones a nivel de campo y lógica de integridad referencial.
2.  **Capa de Repositorios (Repositories)**: Abstrae el acceso a los datos. Todas las consultas ORM complejas se centralizan aquí para evitar que la lógica de persistencia se disperse por los servicios o las vistas.
3.  **Capa de Servicios (Services)**: Contiene la lógica de negocio pura. Orquestan las operaciones entre múltiples repositorios y aseguran que se cumplan las reglas del sistema.
4.  **Capa de API (REST API)**: Gestiona la entrada y salida de datos a través de protocolos HTTP. Utiliza Django REST Framework para la serialización y el control de acceso.

## Organización del Directorio apps/

El núcleo del sistema reside en la carpeta `apps/`, donde cada subcarpeta representa un dominio de negocio específico:

- **academic/**: Gestión de mallas curriculares, materias, paralelos y periodos lectivos.
- **accounts/**: Gestión de usuarios, roles y autenticación.
- **core/**: Utilidades transversales, helpers globales y lógica compartida por todos los módulos.
- **config/**: Configuraciones globales del sistema y parámetros académicos.
- **grading/**: Registro de calificaciones, asistencia e incidentes de conducta.
- **institutions/**: Información de la institución educativa y sus sedes.
- **scheduling/**: Gestión de horarios y disponibilidad docente.
- **students/**: Administración de expedientes de estudiantes, representantes y contactos de emergencia.

## Estructura Estándar de un Módulo

Cada aplicación dentro de `apps/` mantiene la siguiente estructura:

```text
nombre_del_modulo/
├── api/                      # Controladores HTTP y Serializadores
│   ├── serializers.py        # Transformación de datos JSON
│   ├── views.py              # Lógica de los endpoints
│   └── urls.py               # Definición de rutas del módulo
├── models/                   # Definición de entidades de base de datos
│   ├── __init__.py           # Re-exportación de modelos
│   └── modelo_especifico.py  # Archivos individuales por entidad
├── repositories/             # Consultas y persistencia
│   └── modulo_repo.py
├── services/                 # Lógica de negocio y orquestación
│   └── modulo_service.py
├── tests/                    # Pruebas automatizadas
│   ├── test_models.py
│   ├── test_services.py
│   └── test_api.py
├── admin.py                  # Integración con el panel de administración
├── urls.py                   # Punto de entrada de rutas
└── README.md                 # Documentación específica del dominio
```

## Estándares de Codificación

- **Nomenclatura**: Se utiliza `Camel_Case` para los nombres de los modelos de base de datos para mantener consistencia con el esquema histórico, mientras que para variables y métodos se utiliza `snake_case`.
- **Respuestas de API**: Todos los endpoints deben retornar una estructura JSON estandarizada utilizando las utilidades de `apps.core.utils`. Los códigos de estado deben ser semánticos (200 para éxito, 201 para creación).
    ```json
    {
      "ok": boolean,
      "data": object | array,
      "msg": string
    }
    ```
- **Persistencia**: Se prohíbe el uso de `Model.objects.query()` directamente en las vistas o servicios. Estas llamadas deben residir exclusivamente en la capa de repositorios.
