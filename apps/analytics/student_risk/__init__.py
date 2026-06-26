# Student Risk sub-app para riesgo estudiantil.

__all__ = [
    "RiskFactor",
    "StudentRiskScore",
    "StudentRiskFactor",
    "StudentFeatureSnapshot",
    "RiskScoringConfig",
    "RiskFactorRepository",
    "StudentRiskScoreRepository",
    "StudentRiskFactorRepository",
    "StudentFeatureSnapshotRepository",
    "RiskScoringConfigRepository",
    "AnalyticsService",
    "StudentRiskCalculationService",
    "RiskScoringConfigService",
]

_MODELS = {
    "RiskFactor",
    "StudentRiskScore",
    "StudentRiskFactor",
    "StudentFeatureSnapshot",
    "RiskScoringConfig",
}
_REPOSITORIES = {
    "RiskFactorRepository",
    "StudentRiskScoreRepository",
    "StudentRiskFactorRepository",
    "StudentFeatureSnapshotRepository",
    "RiskScoringConfigRepository",
}
_SERVICES = {
    "AnalyticsService",
    "StudentRiskCalculationService",
    "RiskScoringConfigService",
}


def __getattr__(name):
    if name in _MODELS:
        from .infrastructure import models

        return getattr(models, name)
    if name in _REPOSITORIES:
        from .infrastructure import repositories

        return getattr(repositories, name)
    if name in _SERVICES:
        from .domain import services

        return getattr(services, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
