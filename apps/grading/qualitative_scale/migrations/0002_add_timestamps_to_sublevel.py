from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("grading_qualitative_scale", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="qualitativescalesublevel",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                default=None,
                verbose_name="Fecha de Creaci\u00f3n",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="qualitativescalesublevel",
            name="updated_at",
            field=models.DateTimeField(
                auto_now=True,
                default=None,
                verbose_name="Fecha de Actualizaci\u00f3n",
            ),
            preserve_default=False,
        ),
    ]
