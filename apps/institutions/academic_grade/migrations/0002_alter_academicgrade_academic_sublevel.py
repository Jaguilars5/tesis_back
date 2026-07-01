from django.db import migrations, models
import django.db.models.deletion


def remove_null_sublevel_grades(apps, schema_editor):
    AcademicGrade = apps.get_model("institutions_academic_grade", "AcademicGrade")
    AcademicGrade.objects.filter(academic_sublevel__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("institutions_academic_grade", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(remove_null_sublevel_grades, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="academicgrade",
            name="academic_sublevel",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="institutions_academic_sublevel.academicsublevel",
                verbose_name="Subnivel Academico",
            ),
        ),
    ]
