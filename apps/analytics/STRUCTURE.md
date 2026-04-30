# Estructura del Módulo Analytics

```
analytics/
├─ api/                          # REST API
├─ models/                       # Capa de Datos
│  ├─ student_feature_snapshot.py
│  └─ student_risk_score.py
├─ repositories/                 # Capa de Acceso
└─ services/                     # Capa de Lógica
```

## Estándares de Importación
```python
from apps.analytics.models import StudentRiskScore
from apps.analytics.services import AnalyticsService
```
