from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("grading_evaluation", "0001_initial"),
        ("iam", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="EvaluativeActivityChangeHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("previous_due_date", models.DateField(verbose_name="Fecha de entrega anterior")),
                ("new_due_date", models.DateField(verbose_name="Nueva fecha de entrega")),
                ("reason", models.TextField(blank=True, default="", verbose_name="Razón del cambio")),
                ("modified_at", models.DateTimeField(auto_now_add=True, verbose_name="Modificado en")),
                (
                    "evaluative_activity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="change_history",
                        to="grading_evaluation.evaluativeactivity",
                        verbose_name="Actividad evaluativa",
                    ),
                ),
                (
                    "modified_by_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="iam.user",
                        verbose_name="Modificado por",
                    ),
                ),
            ],
            options={
                "verbose_name": "Historial de cambio de actividad evaluativa",
                "verbose_name_plural": "Historiales de cambio de actividad evaluativa",
                "ordering": ["-modified_at"],
                "indexes": [
                    models.Index(fields=["evaluative_activity", "modified_at"], name="grading_eva_evaluat_a1b2c3_idx"),
                    models.Index(fields=["modified_by_user", "modified_at"], name="grading_eva_modifie_d4e5f6_idx"),
                ],
            },
        ),
    ]
