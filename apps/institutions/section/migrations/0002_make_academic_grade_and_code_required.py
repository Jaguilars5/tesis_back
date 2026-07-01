from django.db import migrations, models
import django.db.models.deletion


def remove_null_academic_grade_sections(apps, schema_editor):
    Section = apps.get_model("institutions_section", "Section")
    Section.objects.filter(academic_grade__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("institutions_section", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(remove_null_academic_grade_sections, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="section",
            name="academic_grade",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="institutions_academic_grade.academicgrade",
                verbose_name="Grado Academico",
            ),
        ),
        migrations.AlterField(
            model_name="section",
            name="code",
            field=models.CharField(db_index=True, max_length=50, verbose_name="Codigo"),
        ),
    ]
