import logging

from django.core.management.base import BaseCommand
from ...ml.train_model import RiskModelTrainer


class Command(BaseCommand):
    help = (
        "Entrena el modelo de regresión logística para riesgo académico. "
        "Usa TODOS los períodos históricos. Target: is_failing (PeriodGradeSummary)."
    )

    def handle(self, *args, **options):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
        trainer = RiskModelTrainer()
        try:
            trainer.train()
            self.stdout.write(self.style.SUCCESS("Modelo entrenado exitosamente"))
        except ValueError as e:
            self.stdout.write(self.style.WARNING(str(e)))
