# Generated manually for consistency
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('institutions_academic_sublevel', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicGrade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creaci\u00f3n')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualizaci\u00f3n')),
                ('code', models.CharField(blank=True, db_index=True, max_length=50, verbose_name='C\u00f3digo')),
                ('name', models.CharField(max_length=100, verbose_name='Nombre del Grado')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activo')),
                ('academic_sublevel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='institutions_academic_sublevel.academicsublevel', verbose_name='Subnivel Acad\u00e9mico')),
            ],
            options={
                'verbose_name': 'Grado Acad\u00e9mico',
                'verbose_name_plural': 'Grados Acad\u00e9micos',
                'ordering': ['name'],
            },
        ),
    ]
