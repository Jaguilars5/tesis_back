from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("academic_period", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="academicperiod",
            name="grades_locked",
            field=models.BooleanField(
                default=False,
                help_text="Si está activo, no se permiten cambios de notas ni actividades en este período.",
                verbose_name="Calificaciones cerradas",
            ),
        ),
    ]
