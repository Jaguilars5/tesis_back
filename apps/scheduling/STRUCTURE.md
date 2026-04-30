# Estructura del Módulo Scheduling

```
scheduling/
├─ api/                          # Capa HTTP
│  ├─ serializers.py
│  ├─ urls.py
│  └─ views.py
│
├─ models/                       # Capa de Datos (Tablas)
│  ├─ schedule_slot.py
│  ├─ schedule_template_config.py
│  ├─ subject_constraint.py
│  ├─ teacher_availability.py
│  └─ time_slot.py
│
├─ repositories/                 # Capa de Acceso (Queries)
│  └─ scheduling_repo.py
│
├─ services/                     # Capa de Lógica (Reglas)
│  └─ scheduling_service.py
│
├─ admin.py                      # Panel de control
└─ README.md                     # Documentación general
```

## Responsabilidades

- **Models**: Definen la estructura y validaciones de nivel campo.
- **Repositories**: Encapsulan el uso del ORM de Django.
- **Services**: Implementan la lógica de negocio multimodelo y validación de conflictos.
- **API**: Exponen la funcionalidad mediante endpoints REST estandarizados.

## Estándares de Importación

### Recomendado
```python
from apps.scheduling.models import TimeSlot
from apps.scheduling.services import SchedulingService
```

### No Recomendado
```python
from apps.scheduling.models.time_slot import TimeSlot # Importar del archivo directo
```
