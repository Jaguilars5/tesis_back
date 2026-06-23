"""
Seed idempotente del singleton de configuración del motor de riesgo (Fase 5).

Crea (si no existe) la fila singleton con el preset por defecto "Equilibrado",
cuyos valores replican exactamente el comportamiento histórico (WEIGHTS + umbrales
de Fase 0). NO sobrescribe una configuración existente (para no pisar ajustes de
la institución). Usa `--reset` para forzar los valores del preset por defecto.
"""

from django.core.management.base import BaseCommand

from apps.analytics.models import RiskScoringConfig
from apps.analytics.services.risk_scoring_config_service import DEFAULT_PRESET, PRESETS


class Command(BaseCommand):
    help = "Crea la configuración global del motor de riesgo con el preset por defecto."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Restablece la configuración a los valores del preset por defecto.",
        )
        parser.add_argument(
            "--preset",
            type=str,
            default=DEFAULT_PRESET,
            choices=list(PRESETS.keys()),
            help="Preset a sembrar (por defecto: equilibrado).",
        )

    def handle(self, *args, **options):
        preset_key = options["preset"]
        reset = options["reset"]
        preset = PRESETS[preset_key]

        existing = RiskScoringConfig.objects.filter(
            pk=RiskScoringConfig.SINGLETON_PK
        ).first()

        if existing and not reset:
            self.stdout.write(
                self.style.WARNING(
                    "La configuración del motor de riesgo ya existe. "
                    "Usa --reset para restablecerla."
                )
            )
            return

        config, created = RiskScoringConfig.objects.update_or_create(
            pk=RiskScoringConfig.SINGLETON_PK,
            defaults={**preset, "preset": preset_key},
        )

        action = "creada" if created else "restablecida"
        self.stdout.write(
            self.style.SUCCESS(
                f"Configuración del motor de riesgo {action} con preset '{preset_key}'."
            )
        )
