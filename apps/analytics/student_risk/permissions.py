"""
Permisos para el módulo de riesgo estudiantil.

Mapea acciones del ViewSet a códigos de permiso del sistema.
"""

from apps.core.constants.permissions import analytics

# StudentRiskScore ViewSet
RISK_SCORE_ACTION_PERMISSIONS = {
    "list": analytics.VIEW_RISK_SCORE,
    "get": analytics.VIEW_RISK_SCORE,
    "create": analytics.CREATE_STUDENT_RISK_FACTOR,
    "update": analytics.UPDATE_STUDENT_RISK_FACTOR,
    "destroy": analytics.DELETE_STUDENT_RISK_FACTOR,
    "calculate": analytics.CREATE_STUDENT_RISK_FACTOR,
    "batch_calculate": analytics.CREATE_STUDENT_RISK_FACTOR,
}

# RiskFactor ViewSet (readonly)
RISK_FACTOR_ACTION_PERMISSIONS = {
    "list": analytics.VIEW_RISK_FACTOR,
    "get": analytics.VIEW_RISK_FACTOR,
}

# StudentRiskFactor ViewSet (readonly)
STUDENT_RISK_FACTOR_ACTION_PERMISSIONS = {
    "list": analytics.VIEW_STUDENT_RISK_FACTOR,
    "get": analytics.VIEW_STUDENT_RISK_FACTOR,
}

# StudentFeatureSnapshot ViewSet
FEATURE_SNAPSHOT_ACTION_PERMISSIONS = {
    "list": analytics.VIEW_FEATURE_SNAPSHOT,
    "get": analytics.VIEW_FEATURE_SNAPSHOT,
}

# RiskScoringConfig ViewSet
SCORING_CONFIG_ACTION_PERMISSIONS = {
    "list": analytics.VIEW_SCORING_CONFIG,
    "update_config": analytics.UPDATE_SCORING_CONFIG,
    "apply_preset": analytics.UPDATE_SCORING_CONFIG,
}
