import logging

from django.core.management.base import BaseCommand
from ...ml.train_model import RiskModelTrainer


class Command(BaseCommand):
    help = "Entrena el modelo ML de riesgo académico"

    def add_arguments(self, parser):
        parser.add_argument("--period-id", type=int, help="ID del período académico")

    def handle(self, *args, **options):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
        trainer = RiskModelTrainer()
        try:
            trainer.train(period_id=options.get("period_id"))
            self.stdout.write(self.style.SUCCESS("Modelo entrenado exitosamente"))
        except ValueError as e:
            self.stdout.write(self.style.WARNING(str(e)))
