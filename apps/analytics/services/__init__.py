"""
Servicios transversales (no específicos de una entidad) del módulo Analytics.

La lógica por entidad vive en cada bounded context (student_risk, dashboard,
early_alert). Aquí sólo quedan servicios compartidos / de infraestructura:

- ``AcademicRiskFeatureBuilder``: construye el snapshot de features leyendo
  asistencia, conducta y calificaciones (cross-app).
- ``RiskScoringConfigService`` / ``EffectiveScoringConfig``: lectura+normalización
  de la configuración efectiva del motor de riesgo.
- ``StudentClusteringService``: clustering KMeans.
- ``AnalyticsService``: lecturas agregadas del perfil de riesgo.
"""

from .analytics_service import AnalyticsService
from .clustering_service import StudentClusteringService
from .feature_builder import AcademicRiskFeatureBuilder
from .risk_scoring_config_service import (
    DEFAULT_CONFIG,
    DEFAULT_PRESET,
    PRESETS,
    EffectiveScoringConfig,
    RiskScoringConfigService,
)

__all__ = [
    "AcademicRiskFeatureBuilder",
    "AnalyticsService",
    "StudentClusteringService",
    "RiskScoringConfigService",
    "EffectiveScoringConfig",
    "DEFAULT_CONFIG",
    "DEFAULT_PRESET",
    "PRESETS",
]
