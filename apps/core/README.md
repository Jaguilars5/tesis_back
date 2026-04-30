# Módulo Core

El módulo `core` contiene componentes transversales y utilidades globales que son utilizadas por múltiples aplicaciones dentro del proyecto. Su objetivo es reducir la duplicación de código y centralizar la lógica técnica que no pertenece a un dominio de negocio específico.

## Utilidades de API

### Respuestas Estandarizadas (`apps.core.utils.responses`)

Proporciona funciones para asegurar que todas las respuestas de la API sigan el formato unificado requerido por el sistema.

#### `ok_response(data, status=200)`
Retorna una respuesta exitosa.
- **data**: El cuerpo de datos (diccionario o lista).
- **status**: Código de estado HTTP (opcional, por defecto 200). Use 201 para creaciones exitosas.

#### `error_response(msg, status=400)`
Retorna una respuesta de error.
- **msg**: Descripción del error (string o excepción).
- **status**: Código de estado HTTP (opcional, por defecto 400).

## Estándares de Uso

1. **Importación**: Siempre importe desde el paquete de utilidades:
   ```python
   from apps.core.utils import ok_response, error_response
   ```
2. **Consistencia**: No utilice la clase `Response` de DRF directamente en las vistas a menos que sea estrictamente necesario para un comportamiento no estándar (como descarga de archivos).
3. **Mantenimiento**: Cualquier lógica que se repita en más de dos módulos de negocio debería ser evaluada para su promoción al módulo `core`.
