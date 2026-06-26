from django.db import migrations


def set_db_level_defaults(apps, schema_editor):
    """Fija defaults a nivel de PostgreSQL como red de seguridad.

    Django solo aplica `default` en la capa Python, por lo que cualquier escritura
    que se salte el constructor del modelo (`QuerySet.update()`, SQL crudo,
    `bulk_create`, etc.) puede dejar estas columnas NOT NULL en NULL. Fijar el
    default en la base de datos evita ese NOT NULL violation. Se omite en motores
    que no son PostgreSQL (p. ej. SQLite en tests).
    """
    if schema_editor.connection.vendor != "postgresql":
        return
    table = "grading_student_note_studentnote"
    schema_editor.execute(
        f"ALTER TABLE {table} ALTER COLUMN grading_mode SET DEFAULT 'NUMERIC'"
    )
    schema_editor.execute(
        f"ALTER TABLE {table} ALTER COLUMN manually_overridden SET DEFAULT false"
    )


def drop_db_level_defaults(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    table = "grading_student_note_studentnote"
    schema_editor.execute(f"ALTER TABLE {table} ALTER COLUMN grading_mode DROP DEFAULT")
    schema_editor.execute(
        f"ALTER TABLE {table} ALTER COLUMN manually_overridden DROP DEFAULT"
    )


class Migration(migrations.Migration):

    dependencies = [
        ("grading_student_note", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(set_db_level_defaults, drop_db_level_defaults),
    ]
