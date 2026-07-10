import logging

from django.core.management.base import BaseCommand, CommandParser
from ...ml.train_model import RiskModelTrainer
from ...ml.subject_model import SubjectRiskModelTrainer


class Command(BaseCommand):
    help = (
        "Entrena modelos de riesgo académico. Por defecto entrena el modelo "
        "general por estudiante. Con --subject-models entrena modelos por materia."
    )

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            "--subject-models",
            action="store_true",
            dest="subject_models",
            help="Entrena modelos por materia (modelo_riesgo_materia)",
        )
        parser.add_argument(
            "--subject-code",
            type=str,
            default=None,
            help="C\u00f3digo de materia espec\u00edfica (ej: MAT). Si se omite, entrena todas.",
        )

    def handle(self, *args, **options):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )

        if options.get("subject_models"):
            self._train_subject_models(options.get("subject_code"))
        else:
            self._train_general_model()

    def _train_general_model(self):
        trainer = RiskModelTrainer()
        try:
            trainer.train()
            self.stdout.write(self.style.SUCCESS("Modelo general entrenado exitosamente"))
        except ValueError as e:
            self.stdout.write(self.style.WARNING(str(e)))

    def _train_subject_models(self, subject_code=None):
        trainer = SubjectRiskModelTrainer()
        if subject_code:
            if subject_code.upper() not in [
                "MAT", "FIS", "QUI", "BIO", "LEN", "ING", "SOC", "FIL", "EDU_FIS", "EDU_ART"
            ]:
                self.stdout.write(self.style.ERROR(f"C\u00f3digo de materia inv\u00e1lido: {subject_code}"))
                return
            model = trainer.train_subject(subject_code.upper())
            if model:
                self.stdout.write(self.style.SUCCESS(f"Modelo para {subject_code.upper()} entrenado exitosamente"))
            else:
                self.stdout.write(self.style.WARNING(f"No se pudo entrenar modelo para {subject_code.upper()}"))
        else:
            results = trainer.train_all_subjects()
            trained = [code for code, ok in results.items() if ok]
            self.stdout.write(
                self.style.SUCCESS(f"Modelos por materia entrenados: {len(trained)}/10")
            )
            for code in trained:
                self.stdout.write(f"  - {code}")
