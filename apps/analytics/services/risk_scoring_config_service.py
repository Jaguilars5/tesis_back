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
        "attendance_green_min": 85.01,
        "average_red_max": 6.0,
        "average_yellow_max": 7.0,
        "average_green_min": 7.01,
        "severe_red_min": 3,
        "mild_yellow_min": 5,
        "severe_green_max": 0,
        "mild_green_max": 5,
        "score_red_min": 70,
        "score_yellow_min": 40,
    },
    # Conservador: más sensible (clasifica en riesgo antes) → umbrales más altos.
    "conservador": {
        "engine": "reglas",
        "weight_conducta": 25,
        "weight_asistencia": 40,
        "weight_calificaciones": 35,
        "attendance_red_max": 75,
        "attendance_yellow_max": 90,
        "attendance_green_min": 95,
        "average_red_max": 6.5,
        "average_yellow_max": 7.5,
        "average_green_min": 8.0,
        "severe_red_min": 2,
        "mild_yellow_min": 4,
        "severe_green_max": 0,
        "mild_green_max": 4,
        "score_red_min": 68,
        "score_yellow_min": 38,
    },
    # Estricto: menos sensible (sólo casos extremos en rojo) → umbrales más bajos.
    "estricto": {
        "engine": "reglas",
        "weight_conducta": 35,
        "weight_asistencia": 30,
        "weight_calificaciones": 35,
        "attendance_red_max": 60,
        "attendance_yellow_max": 80,
        "attendance_green_min": 85,
        "average_red_max": 5.0,
        "average_yellow_max": 6.5,
        "average_green_min": 7.0,
        "severe_red_min": 4,
        "mild_yellow_min": 6,
        "severe_green_max": 0,
        "mild_green_max": 6,
        "score_red_min": 72,
        "score_yellow_min": 42,
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
    attendance_green_min: float
    average_red_max: float
    average_yellow_max: float
    average_green_min: float
    severe_red_min: int
    mild_yellow_min: int
    severe_green_max: int
    mild_green_max: int
    # Umbrales del puntaje final (0–100) para clasificación rojo/amarillo/verde
    score_red_min: float
    score_yellow_min: float
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
    score_red_min=70.0,
    score_yellow_min=40.0,
    attendance_red_max=70.0,
    attendance_yellow_max=85.0,
    attendance_green_min=85.01,
    average_red_max=6.0,
    average_yellow_max=7.0,
    average_green_min=7.01,
    severe_red_min=3,
    mild_yellow_min=5,
    severe_green_max=0,
    mild_green_max=5,
    source="default",
    version_tag="",
)


class RiskScoringConfigService:
    """Lectura de la configuración del motor de riesgo."""

    @staticmethod
    def build_effective_from_dict(
        data: dict | None = None,
        *,
        source: str = "simulate",
        version_tag: str = "simulate",
    ) -> EffectiveScoringConfig:
        """
        Construye una config efectiva a partir de un dict (preset + overrides).

        Usado por el simulador para probar pesos/umbrales sin persistir en BD.
        Los pesos del dict están en porcentaje (suman ~100).
        """
        data = dict(data or {})
        preset = data.pop("preset", None)
        if preset and preset in PRESETS and preset != "personalizado":
            merged = {**PRESETS[preset], **data}
        else:
            base = RiskScoringConfigService.get_effective()
            merged = {
                "engine": base.engine,
                "weight_conducta": base.weight_conducta * 100,
                "weight_asistencia": base.weight_asistencia * 100,
                "weight_calificaciones": base.weight_calificaciones * 100,
                "attendance_red_max": base.attendance_red_max,
                "attendance_yellow_max": base.attendance_yellow_max,
                "attendance_green_min": base.attendance_green_min,
                "average_red_max": base.average_red_max,
                "average_yellow_max": base.average_yellow_max,
                "average_green_min": base.average_green_min,
                "severe_red_min": base.severe_red_min,
                "mild_yellow_min": base.mild_yellow_min,
                "severe_green_max": base.severe_green_max,
                "mild_green_max": base.mild_green_max,
                "score_red_min": base.score_red_min,
                "score_yellow_min": base.score_yellow_min,
                "severe_red_min": base.severe_red_min,
                "mild_yellow_min": base.mild_yellow_min,
                **data,
            }

        wc = float(merged.get("weight_conducta", 30))
        wa = float(merged.get("weight_asistencia", 35))
        wg = float(merged.get("weight_calificaciones", 35))
        total = wc + wa + wg
        if total <= 0:
            wc, wa, wg, total = 30.0, 35.0, 35.0, 100.0

        return EffectiveScoringConfig(
            engine=str(merged.get("engine", "reglas")),
            weight_conducta=wc / total,
            weight_asistencia=wa / total,
            weight_calificaciones=wg / total,
            score_red_min=float(merged.get("score_red_min", 70)),
            score_yellow_min=float(merged.get("score_yellow_min", 40)),
            attendance_red_max=float(merged.get("attendance_red_max", 70)),
            attendance_yellow_max=float(merged.get("attendance_yellow_max", 85)),
            attendance_green_min=float(merged.get("attendance_green_min", 85.01)),
            average_red_max=float(merged.get("average_red_max", 6.0)),
            average_yellow_max=float(merged.get("average_yellow_max", 7.0)),
            average_green_min=float(merged.get("average_green_min", 7.01)),
            severe_red_min=int(merged.get("severe_red_min", 3)),
            mild_yellow_min=int(merged.get("mild_yellow_min", 5)),
            severe_green_max=int(merged.get("severe_green_max", 0)),
            mild_green_max=int(merged.get("mild_green_max", 5)),
            source=source,
            version_tag=version_tag,
        )

    @staticmethod
    def effective_from_db_model(config) -> EffectiveScoringConfig:
        """Normaliza el modelo singleton de BD a EffectiveScoringConfig."""
        total = (
            float(config.weight_conducta)
            + float(config.weight_asistencia)
            + float(config.weight_calificaciones)
        )
        if total <= 0:
            return DEFAULT_CONFIG

        return EffectiveScoringConfig(
            engine=config.engine,
            weight_conducta=float(config.weight_conducta) / total,
            weight_asistencia=float(config.weight_asistencia) / total,
            weight_calificaciones=float(config.weight_calificaciones) / total,
            score_red_min=float(config.score_red_min),
            score_yellow_min=float(config.score_yellow_min),
            attendance_red_max=float(config.attendance_red_max),
            attendance_yellow_max=float(config.attendance_yellow_max),
            attendance_green_min=float(config.attendance_green_min),
            average_red_max=float(config.average_red_max),
            average_yellow_max=float(config.average_yellow_max),
            average_green_min=float(config.average_green_min),
            severe_red_min=int(config.severe_red_min),
            mild_yellow_min=int(config.mild_yellow_min),
            severe_green_max=int(config.severe_green_max),
            mild_green_max=int(config.mild_green_max),
            source="db",
            version_tag=f"cfg{config.pk}u{int(config.updated_at.timestamp())}",
        )

    @staticmethod
    def _normalize_config(config=None) -> EffectiveScoringConfig:
        """Acepta None, EffectiveScoringConfig, modelo BD o dict de overrides."""
        if config is None:
            return RiskScoringConfigService.get_effective()
        if isinstance(config, EffectiveScoringConfig):
            return config
        if isinstance(config, dict):
            return RiskScoringConfigService.build_effective_from_dict(config)
        if hasattr(config, "weight_conducta"):
            return RiskScoringConfigService.effective_from_db_model(config)
        return RiskScoringConfigService.get_effective()

    @staticmethod
    def get_effective() -> EffectiveScoringConfig:
        """
        Devuelve la configuración efectiva.

        - Si existe la fila singleton en BD, la normaliza (pesos a fracciones).
        - Si no existe o la BD no está accesible, devuelve `DEFAULT_CONFIG`
          (mismos valores que el comportamiento histórico → baseline intacto).
        """
        try:
            from apps.analytics.student_risk.infrastructure.repositories import (
                RiskScoringConfigRepository,
            )

            config = RiskScoringConfigRepository.get_singleton()
        except Exception:
            # SimpleTestCase / BD no disponible / tabla aún sin migrar.
            return DEFAULT_CONFIG

        if config is None:
            return DEFAULT_CONFIG

        return RiskScoringConfigService.effective_from_db_model(config)
