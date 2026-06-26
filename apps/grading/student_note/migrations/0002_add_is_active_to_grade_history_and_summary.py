from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("grading_student_note", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="gradechangehistory",
            name="is_active",
            field=models.BooleanField(default=True, verbose_name="Activo"),
        ),
        migrations.AddField(
            model_name="periodgradesummary",
            name="is_active",
            field=models.BooleanField(default=True, verbose_name="Activo"),
        ),
    ]
