"""
Sincroniza risk_label con risk_score en todos los StudentRiskScore existentes.

Útil tras corregir la lógica del semáforo o si hay registros con etiqueta
desincronizada del puntaje (p. ej. 100/100 con «Riesgo Moderado»).

Ejecutar: python manage.py sync_risk_labels
"""

from django.core.management.base import BaseCommand

from apps.analytics.student_risk.domain.risk_engine import score_to_risk_label
from apps.analytics.student_risk.infrastructure.models import StudentRiskScore


class Command(BaseCommand):
    help = "Alinea risk_label con risk_score según umbrales 70/40 del semáforo."

    def handle(self, *args, **options):
        updated = 0
        for score in StudentRiskScore.objects.iterator():
            expected = score_to_risk_label(float(score.risk_score))
            if score.risk_label != expected:
                score.risk_label = expected
                score.save(update_fields=["risk_label", "updated_at"])
                updated += 1

        total = StudentRiskScore.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Etiquetas sincronizadas: {updated} actualizados de {total} registros."
            )
        )
