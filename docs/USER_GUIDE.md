# Guía de Usuario y Manual Técnico

Este documento proporciona instrucciones detalladas sobre el uso y la integración con el backend del sistema de gestión académica.

## Protocolo de Comunicación API

El sistema implementa una interfaz RESTful bajo un protocolo de comunicación estricto para asegurar la predictibilidad y seguridad de las transacciones.

### Requisitos de las Peticiones

1.  **Método HTTP**:
    - Todos los módulos usan métodos HTTP estándar de REST: `GET` para listar/obtener, `POST` para crear, `PUT/PATCH` para actualizar, `DELETE` para eliminar.
    - Los módulos `grading`, `scheduling` y `analytics` usan `POST` para todas las operaciones, enviando parámetros en el cuerpo JSON.
2.  **Cuerpo de la Petición**: Los datos deben enviarse en formato JSON (`application/json`).
3.  **Encabezados de Autenticación**: Las rutas protegidas requieren un token de acceso JWT en el encabezado `Authorization`:
    `Authorization: Bearer <token_de_acceso>`

### Formato de Respuesta Estándar

Independientemente del resultado de la operación, el servidor siempre responderá con un cuerpo JSON estructurado. Los códigos de estado HTTP son semánticos:
- **200 OK**: Operación exitosa (lectura, actualización, eliminación).
- **201 Created**: Recurso creado exitosamente.
- **400 Bad Request**: Error de validación o lógica de negocio.
- **401 Unauthorized**: Error de autenticación.
- **404 Not Found**: Recurso no encontrado.

Estructura del JSON:
- **ok**: Valor booleano que indica si la operación fue exitosa.
- **data**: Contiene el objeto o arreglo de datos resultante.
- **msg**: Mensaje descriptivo. Si `ok` es falso, este campo contendrá la razón del error.

## Gestión de Sesiones

### Inicio de Sesión
Endpoint: `POST /api/accounts/login/`
Payload: `{"email": "usuario@ejemplo.com", "password": "password"}`
Respuesta: Retorna un `access` token y un `refresh` token.

### Renovación de Token
Endpoint: `POST /api/accounts/refresh/`
Payload: `{"refresh": "token_previo"}`
Respuesta: Retorna un nuevo `access` token y los datos actualizados del `user`.

## Flujos de Trabajo Comunes

### Registro de Estudiantes y Representantes

1.  **Creación del Estudiante**: Utilizar el endpoint `POST /api/students/student/`. Es obligatorio asignar una sección académica válida.
2.  **Creación del Representante**: Utilizar el endpoint `POST /api/students/representative/`. El perfil del representante es independiente del estudiante.
3.  **Vinculación**: Utilizar el endpoint `POST /api/students/student-representative/` para crear la relación entre ambos. En este paso se define el parentesco (`kinship`) y los permisos de autorización.

### Gestión Académica

1.  **Configuración del Periodo**: Los administradores deben definir los periodos académicos y actividades (exámenes, tareas) antes de registrar notas.
2.  **Asignación Docente**: Un docente debe estar vinculado a una materia y sección específica para poder registrar calificaciones o asistencia.
3.  **Sincronización Offline**: Los endpoints de estudiantes y notas soportan campos de sincronización (`uuid`, `sync_status`, `sync_version`). El cliente debe gestionar estos campos para la reconciliación de datos registrados sin conexión.

## Solución de Problemas

-   **Error 401 Unauthorized**: El token ha expirado o no es válido. Debe realizarse una renovación mediante el `refresh_token`.
-   **Error 400 Bad Request**: El payload enviado no cumple con las validaciones del modelo o faltan campos obligatorios. Revise el campo `msg` en la respuesta JSON para más detalles.
-   **Conflicto de Sincronización**: Si el `sync_version` en el servidor es mayor al enviado por el cliente, la actualización será rechazada para proteger la integridad de los datos.
