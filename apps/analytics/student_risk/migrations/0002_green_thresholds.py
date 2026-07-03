from decimal import Decimal

from django.db import migrations, models


def set_green_defaults(apps, schema_editor):
    RiskScoringConfig = apps.get_model("student_risk", "RiskScoringConfig")
    for row in RiskScoringConfig.objects.all():
        row.attendance_green_min = max(
            Decimal(str(row.attendance_yellow_max)) + Decimal("0.01"),
            Decimal("85.01"),
        )
        row.average_green_min = max(
            Decimal(str(row.average_yellow_max)) + Decimal("0.01"),
            Decimal("7.01"),
        )
        row.severe_green_max = 0
        row.mild_green_max = row.mild_yellow_min
        row.save(
            update_fields=[
                "attendance_green_min",
                "average_green_min",
                "severe_green_max",
                "mild_green_max",
            ]
        )


class Migration(migrations.Migration):

    dependencies = [
        ("student_risk", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="riskscoringconfig",
            name="attendance_green_min",
            field=models.DecimalField(
                decimal_places=2,
                default=85.01,
                max_digits=5,
                verbose_name="Asistencia mínima para Verde (%)",
            ),
        ),
        migrations.AddField(
            model_name="riskscoringconfig",
            name="average_green_min",
            field=models.DecimalField(
                decimal_places=2,
                default=7.01,
                max_digits=4,
                verbose_name="Promedio mínimo para Verde",
            ),
        ),
        migrations.AddField(
            model_name="riskscoringconfig",
            name="severe_green_max",
            field=models.IntegerField(
                default=0,
                verbose_name="Faltas graves máximas para Verde (≤)",
            ),
        ),
        migrations.AddField(
            model_name="riskscoringconfig",
            name="mild_green_max",
            field=models.IntegerField(
                default=5,
                verbose_name="Faltas leves máximas para Verde (≤)",
            ),
        ),
        migrations.RunPython(set_green_defaults, migrations.RunPython.noop),
    ]
