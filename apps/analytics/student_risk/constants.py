"""
Constantes para el módulo de riesgo estudiantil.
"""

# Etiquetas de riesgo
RISK_LABEL_GREEN = "verde"
RISK_LABEL_YELLOW = "amarillo"
RISK_LABEL_RED = "rojo"

# Motor de scoring
ENGINE_RULES = "reglas"
ENGINE_ML = "ML"

# Presets
PRESET_CONSERVADOR = "conservador"
PRESET_EQUILIBRADO = "equilibrado"
PRESET_ESTRICTO = "estricto"
PRESET_PERSONALIZADO = "personalizado"

# Factores de riesgo por defecto
DEFAULT_RISK_FACTORS = [
    ("LOW_ATTENDANCE", "Baja Asistencia"),
    ("FAILING_GRADES", "Calificaciones Bajas"),
    ("BEHAVIORAL", "Problemas de Conducta"),
    ("DROPOUT_RISK", "Riesgo de Deserción"),
    ("SOCIOEMOTIONAL", "Problemas Socioemocionales"),
]
