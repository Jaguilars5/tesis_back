# Decorators

Decoradores personalizado para el módulo accounts.

## Contenido

### @require_permission(codename)

Decorador para proteger vistas función-based con un permiso específico.

**Comportamiento:**

- 401 si no hay usuario autenticado (token ausente o inválido)
- 403 si el usuario autenticado no tiene el permiso
- Ejecuta la vista si el usuario tiene el permiso

## Uso

```python
from rest_framework.decorators import api_view
from apps.accounts.decorators import require_permission

@api_view(['POST'])
@require_permission('grading.create_note')
def create_note(request):
    # Usuario garantizado que tiene el permiso
    return Response({'message': 'Nota creada'})
```

## Notas

Para ViewSets de DRF, usa `permission_classes` en su lugar:

```python
from rest_framework.permissions import IsAuthenticated

class MyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
```
