import logging

from django.core.management.base import BaseCommand, CommandParser

from ...ml.annual_model import AnnualRiskModelTrainer
from ...ml.dropout_model import DropoutRiskModelTrainer
from ...ml.subject_model import SubjectRiskModelTrainer
from ...ml.train_model import RiskModelTrainer


class Command(BaseCommand):
    help = (
        "Entrena modelos de riesgo. Por defecto entrena el modelo general por "
        "estudiante. Opciones: --subject-model, --annual-model, --dropout-model."
    )

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            "--subject-model",
            action="store_true",
            dest="subject_model",
            help="Entrena modelo de riesgo por materia",
        )
        parser.add_argument(
            "--annual-model",
            action="store_true",
            dest="annual_model",
            help="Entrena modelo anual de perdida/promocion",
        )
        parser.add_argument(
            "--dropout-model",
            action="store_true",
            dest="dropout_model",
            help="Entrena modelo de riesgo de desercion escolar",
        )

        parser.add_argument("--n-estimators", type=int, dest="n_estimators")
        parser.add_argument("--max-depth", type=int, dest="max_depth")
        parser.add_argument("--min-samples-leaf", type=int, dest="min_samples_leaf")
        parser.add_argument(
            "--class-weight",
            choices=["balanced", "none"],
            dest="class_weight",
        )
        parser.add_argument("--cv-splits", type=int, dest="cv_splits")
        parser.add_argument("--random-state", type=int, dest="random_state")

    def _training_params(self, options):
        fields = (
            "n_estimators",
            "max_depth",
            "min_samples_leaf",
            "class_weight",
            "cv_splits",
            "random_state",
        )
        return {field: options.get(field) for field in fields}

    def handle(self, *args, **options):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )

        if options.get("annual_model"):
            self._train_annual_model(self._training_params(options))
        elif options.get("dropout_model"):
            self._train_dropout_model(self._training_params(options))
        elif options.get("subject_model"):
            self._train_subject_model(self._training_params(options))
        else:
            self._train_general_model(self._training_params(options))

    def _train_general_model(self, training_params=None):
        trainer = RiskModelTrainer()
        try:
            trainer.train(training_params=training_params)
            self.stdout.write(
                self.style.SUCCESS("Modelo general entrenado exitosamente")
            )
        except ValueError as e:
            self.stdout.write(self.style.WARNING(str(e)))

    def _train_subject_model(self, training_params=None):
        trainer = SubjectRiskModelTrainer()
        try:
            trainer.train(training_params=training_params)
            self.stdout.write(
                self.style.SUCCESS("Modelo por materia entrenado exitosamente")
            )
        except ValueError as e:
            self.stdout.write(self.style.WARNING(str(e)))

    def _train_annual_model(self, training_params=None):
        trainer = AnnualRiskModelTrainer()
        try:
            trainer.train(training_params=training_params)
            self.stdout.write(self.style.SUCCESS("Modelo anual entrenado exitosamente"))
        except ValueError as e:
            self.stdout.write(self.style.WARNING(str(e)))

    def _train_dropout_model(self, training_params=None):
        trainer = DropoutRiskModelTrainer()
        try:
            trainer.train(training_params=training_params)
            self.stdout.write(
                self.style.SUCCESS("Modelo de desercion entrenado exitosamente")
            )
        except ValueError as e:
            self.stdout.write(self.style.WARNING(str(e)))
