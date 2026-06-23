"""
Servicio de lectura de la configuración del motor de riesgo (Fase 5, Auditoría §9).

Expone una **configuración efectiva** (dataclass inmutable) que `tasks.py` consume
en lugar de las constantes hardcodeadas. Si no existe fila en BD (o la BD no está
disponible, p. ej. en `SimpleTestCase`), devuelve los **defaults seguros** que
replican exactamente el comportamiento histórico (`WEIGHTS` + umbrales de Fase 0).

Los pesos se almacenan como porcentajes (suman 100) y aquí se normalizan a
fracciones (0–1) para el cálculo ponderado.
"""

from dataclasses import dataclass


# ─── Presets cerrados (punto de partida seguro, Auditoría §9.4) ───
# Pesos en porcentaje (suman 100). Umbrales del semáforo.
PRESETS = {
    "equilibrado": {
        "engine": "reglas",
        "weight_conducta": 30,
        "weight_asistencia": 35,
        "weight_calificaciones": 35,
        "attendance_red_max": 70,
        "attendance_yellow_max": 85,
        "average_red_max": 6.0,
        "average_yellow_max": 7.0,
        "severe_red_min": 3,
        "mild_yellow_min": 5,
    },
    # Conservador: más sensible (clasifica en riesgo antes) → umbrales más altos.
    "conservador": {
        "engine": "reglas",
        "weight_conducta": 25,
        "weight_asistencia": 40,
        "weight_calificaciones": 35,
        "attendance_red_max": 75,
        "attendance_yellow_max": 90,
        "average_red_max": 6.5,
        "average_yellow_max": 7.5,
        "severe_red_min": 2,
        "mild_yellow_min": 4,
    },
    # Estricto: menos sensible (sólo casos extremos en rojo) → umbrales más bajos.
    "estricto": {
        "engine": "reglas",
        "weight_conducta": 35,
        "weight_asistencia": 30,
        "weight_calificaciones": 35,
        "attendance_red_max": 60,
        "attendance_yellow_max": 80,
        "average_red_max": 5.0,
        "average_yellow_max": 6.5,
        "severe_red_min": 4,
        "mild_yellow_min": 6,
    },
}

DEFAULT_PRESET = "equilibrado"


@dataclass(frozen=True)
class EffectiveScoringConfig:
    """Configuración efectiva normalizada que consume el motor de cálculo."""

    engine: str
    # Pesos como fracciones (0–1), suman 1.0
    weight_conducta: float
    weight_asistencia: float
    weight_calificaciones: float
    # Umbrales del semáforo
    attendance_red_max: float
    attendance_yellow_max: float
    average_red_max: float
    average_yellow_max: float
    severe_red_min: int
    mild_yellow_min: int
    # Trazabilidad: identifica el origen de la config para `model_version`.
    source: str = "default"  # "default" | "db"
    version_tag: str = ""

    @property
    def weights(self) -> dict:
        return {
            "conducta": self.weight_conducta,
            "asistencia": self.weight_asistencia,
            "calificaciones": self.weight_calificaciones,
        }


# Defaults seguros: replican EXACTAMENTE el comportamiento de Fase 0
# (WEIGHTS = 0.30/0.35/0.35 y los umbrales de _risk_level).
DEFAULT_CONFIG = EffectiveScoringConfig(
    engine="reglas",
    weight_conducta=0.30,
    weight_asistencia=0.35,
    weight_calificaciones=0.35,
    attendance_red_max=70.0,
    attendance_yellow_max=85.0,
    average_red_max=6.0,
    average_yellow_max=7.0,
    severe_red_min=3,
    mild_yellow_min=5,
    source="default",
    version_tag="",
)


class RiskScoringConfigService:
    """Lectura de la configuración del motor de riesgo."""

    @staticmethod
    def get_effective() -> EffectiveScoringConfig:
        """
        Devuelve la configuración efectiva.

        - Si existe la fila singleton en BD, la normaliza (pesos a fracciones).
        - Si no existe o la BD no está accesible, devuelve `DEFAULT_CONFIG`
          (mismos valores que el comportamiento histórico → baseline intacto).
        """
        try:
            from apps.analytics.repositories.risk_scoring_config_repository import (
                RiskScoringConfigRepository,
            )

            config = RiskScoringConfigRepository.get_singleton()
        except Exception:
            # SimpleTestCase / BD no disponible / tabla aún sin migrar.
            return DEFAULT_CONFIG

        if config is None:
            return DEFAULT_CONFIG

        total = (
            float(config.weight_conducta)
            + float(config.weight_asistencia)
            + float(config.weight_calificaciones)
        )
        # Evitar división por cero ante datos corruptos: caer a defaults.
        if total <= 0:
            return DEFAULT_CONFIG

        return EffectiveScoringConfig(
            engine=config.engine,
            weight_conducta=float(config.weight_conducta) / total,
            weight_asistencia=float(config.weight_asistencia) / total,
            weight_calificaciones=float(config.weight_calificaciones) / total,
            attendance_red_max=float(config.attendance_red_max),
            attendance_yellow_max=float(config.attendance_yellow_max),
            average_red_max=float(config.average_red_max),
            average_yellow_max=float(config.average_yellow_max),
            severe_red_min=int(config.severe_red_min),
            mild_yellow_min=int(config.mild_yellow_min),
            source="db",
            version_tag=f"cfg{config.pk}u{int(config.updated_at.timestamp())}",
        )
