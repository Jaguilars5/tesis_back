import logging

from django.core.management.base import BaseCommand, CommandParser
from ...ml.train_model import RiskModelTrainer
from ...ml.subject_model import SubjectRiskModelTrainer
from ...ml.annual_model import AnnualRiskModelTrainer


class Command(BaseCommand):
    help = (
        "Entrena modelos de riesgo académico. Por defecto entrena el modelo "
        "general por estudiante. Opciones: --subject-model, --annual-model."
    )

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            "--subject-model",
            action="store_true",
            dest="subject_model",
            help="Entrena modelo de riesgo por materia (único)",
        )
        parser.add_argument(
            "--annual-model",
            action="store_true",
            dest="annual_model",
            help="Entrena modelo anual (predice si el estudiante pierde el a\u00f1o)",
        )

    def handle(self, *args, **options):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )

        if options.get("annual_model"):
            self._train_annual_model()
        elif options.get("subject_model"):
            self._train_subject_model()
        else:
            self._train_general_model()

    def _train_general_model(self):
        trainer = RiskModelTrainer()
        try:
            trainer.train()
            self.stdout.write(self.style.SUCCESS("Modelo general entrenado exitosamente"))
        except ValueError as e:
            self.stdout.write(self.style.WARNING(str(e)))

    def _train_subject_model(self):
        trainer = SubjectRiskModelTrainer()
        try:
            trainer.train()
            self.stdout.write(self.style.SUCCESS("Modelo por materia entrenado exitosamente"))
        except ValueError as e:
            self.stdout.write(self.style.WARNING(str(e)))

    def _train_annual_model(self):
        trainer = AnnualRiskModelTrainer()
        try:
            trainer.train()
            self.stdout.write(self.style.SUCCESS("Modelo anual entrenado exitosamente"))
        except ValueError as e:
            self.stdout.write(self.style.WARNING(str(e)))
