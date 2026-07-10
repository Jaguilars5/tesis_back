from decimal import Decimal

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("student_risk", "0002_green_thresholds"),
    ]

    operations = [
        migrations.AddField(
            model_name="riskscoringconfig",
            name="score_red_min",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("70.00"),
                help_text="Los puntajes >= este valor se clasifican como Rojo",
                max_digits=5,
                verbose_name="Puntaje mínimo para Rojo (≥)",
            ),
        ),
        migrations.AddField(
            model_name="riskscoringconfig",
            name="score_yellow_min",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("40.00"),
                help_text="Los puntajes >= este valor y < score_red_min se clasifican como Amarillo",
                max_digits=5,
                verbose_name="Puntaje mínimo para Amarillo (≥)",
            ),
        ),
    ]
