from django.core.management.base import BaseCommand

from apps.accounts.models import Permission
from apps.core.constants.permissions import (
    academic,
    accounts,
    analytics,
    grading,
    institutions,
    scheduling,
    students,
)


def _collect_permissions_from_dataclass(dataclass_obj, module_name):
    permissions = []
    for field_name in dir(dataclass_obj):
        if field_name.isupper():
            value = getattr(dataclass_obj, field_name)
            if isinstance(value, str) and "." in value:
                action = " ".join(
                    w.capitalize() for w in field_name.lower().split("_")[1:]
                )
                description = f"{action} - {module_name}"
                permissions.append((value, description))
    return permissions


def _build_catalog():
    catalog = {}
    modules = [
        ("accounts", accounts),
        ("institutions", institutions),
        ("academic", academic),
        ("students", students),
        ("grading", grading),
        ("scheduling", scheduling),
        ("analytics", analytics),
    ]
    for module_name, perms in modules:
        collected = _collect_permissions_from_dataclass(perms, module_name)

        description_overrides = {
            "accounts.view_user": "Ver usuarios",
            "accounts.create_user": "Crear usuarios",
            "accounts.update_user": "Actualizar usuarios",
            "accounts.delete_user": "Eliminar usuarios",
            "accounts.view_role": "Ver roles",
            "accounts.create_role": "Crear roles",
            "accounts.update_role": "Actualizar roles",
            "accounts.delete_role": "Eliminar roles",
            "accounts.view_permission": "Ver permisos",
            "accounts.create_permission": "Crear permisos",
            "accounts.update_permission": "Actualizar permisos",
            "accounts.delete_permission": "Eliminar permisos",
            "institutions.view_institution": "Ver instituciones",
            "institutions.create_institution": "Crear instituciones",
            "institutions.update_institution": "Actualizar instituciones",
            "institutions.delete_institution": "Eliminar instituciones",
            "institutions.view_school_year": "Ver a\u00f1os escolares",
            "institutions.create_school_year": "Crear a\u00f1os escolares",
            "institutions.update_school_year": "Actualizar a\u00f1os escolares",
            "institutions.delete_school_year": "Eliminar a\u00f1os escolares",
            "institutions.view_classroom": "Ver aulas",
            "institutions.create_classroom": "Crear aulas",
            "institutions.update_classroom": "Actualizar aulas",
            "institutions.delete_classroom": "Eliminar aulas",
            "academic.view_section": "Ver secciones",
            "academic.create_section": "Crear secciones",
            "academic.update_section": "Actualizar secciones",
            "academic.delete_section": "Eliminar secciones",
            "academic.view_subject": "Ver materias",
            "academic.create_subject": "Crear materias",
            "academic.update_subject": "Actualizar materias",
            "academic.delete_subject": "Eliminar materias",
            "academic.view_period": "Ver per\u00edodos acad\u00e9micos",
            "academic.create_period": "Crear per\u00edodos acad\u00e9micos",
            "academic.update_period": "Actualizar per\u00edodos acad\u00e9micos",
            "academic.delete_period": "Eliminar per\u00edodos acad\u00e9micos",
            "academic.view_activity": "Ver actividades acad\u00e9micas",
            "academic.create_activity": "Crear actividades acad\u00e9micas",
            "academic.update_activity": "Actualizar actividades acad\u00e9micas",
            "academic.delete_activity": "Eliminar actividades acad\u00e9micas",
            "academic.view_regime": "Ver reg\u00edmenes de horario",
            "academic.create_regime": "Crear reg\u00edmenes de horario",
            "academic.update_regime": "Actualizar reg\u00edmenes de horario",
            "academic.delete_regime": "Eliminar reg\u00edmenes de horario",
            "academic.view_teacher_subject": "Ver asignaciones docente-materia",
            "academic.create_teacher_subject": "Crear asignaciones docente-materia",
            "academic.update_teacher_subject": "Actualizar asignaciones docente-materia",
            "academic.delete_teacher_subject": "Eliminar asignaciones docente-materia",
            "academic.view_config": "Ver configuraci\u00f3n acad\u00e9mica",
            "academic.create_config": "Crear configuraci\u00f3n acad\u00e9mica",
            "academic.update_config": "Actualizar configuraci\u00f3n acad\u00e9mica",
            "academic.delete_config": "Eliminar configuraci\u00f3n acad\u00e9mica",
            "students.view_student": "Ver estudiantes",
            "students.create_student": "Crear estudiantes",
            "students.update_student": "Actualizar estudiantes",
            "students.delete_student": "Eliminar estudiantes",
            "students.view_representative": "Ver representantes",
            "students.create_representative": "Crear representantes",
            "students.update_representative": "Actualizar representantes",
            "students.delete_representative": "Eliminar representantes",
            "students.view_relationship": "Ver relaciones estudiante-representante",
            "students.create_relationship": "Crear relaciones estudiante-representante",
            "students.update_relationship": "Actualizar relaciones estudiante-representante",
            "students.delete_relationship": "Eliminar relaciones estudiante-representante",
            "grading.view_note": "Ver calificaciones",
            "grading.create_note": "Crear calificaciones",
            "grading.update_note": "Actualizar calificaciones",
            "grading.delete_note": "Eliminar calificaciones",
            "grading.view_attendance": "Ver asistencia",
            "grading.create_attendance": "Crear asistencia",
            "grading.update_attendance": "Actualizar asistencia",
            "grading.delete_attendance": "Eliminar asistencia",
            "grading.view_incident": "Ver incidentes de conducta",
            "grading.create_incident": "Crear incidentes de conducta",
            "grading.update_incident": "Actualizar incidentes de conducta",
            "grading.delete_incident": "Eliminar incidentes de conducta",
            "scheduling.view_schedule": "Ver horarios",
            "scheduling.create_schedule": "Crear horarios",
            "scheduling.update_schedule": "Actualizar horarios",
            "scheduling.delete_schedule": "Eliminar horarios",
            "scheduling.view_timeslot": "Ver bloques de tiempo",
            "scheduling.create_timeslot": "Crear bloques de tiempo",
            "scheduling.update_timeslot": "Actualizar bloques de tiempo",
            "scheduling.delete_timeslot": "Eliminar bloques de tiempo",
            "scheduling.view_availability": "Ver disponibilidad docente",
            "scheduling.create_availability": "Crear disponibilidad docente",
            "scheduling.update_availability": "Actualizar disponibilidad docente",
            "scheduling.delete_availability": "Eliminar disponibilidad docente",
            "scheduling.view_constraint": "Ver restricciones de materias",
            "scheduling.create_constraint": "Crear restricciones de materias",
            "scheduling.update_constraint": "Actualizar restricciones de materias",
            "scheduling.delete_constraint": "Eliminar restricciones de materias",
            "scheduling.view_template": "Ver configuraciones de plantilla",
            "scheduling.create_template": "Crear configuraciones de plantilla",
            "scheduling.update_template": "Actualizar configuraciones de plantilla",
            "scheduling.delete_template": "Eliminar configuraciones de plantilla",
            "analytics.view_risk_score": "Ver puntajes de riesgo",
            "analytics.view_feature_snapshot": "Ver snapshots de caracter\u00edsticas",
        }

        result = []
        for codename, desc in collected:
            result.append(
                (codename, description_overrides.get(codename, desc))
            )
        catalog[module_name] = result
    return catalog


PERMISSIONS_CATALOG = _build_catalog()


class Command(BaseCommand):
    help = "Seed permissions catalog into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--module",
            type=str,
            help="Seed only permissions for a specific module",
        )

    def handle(self, *args, **options):
        module_filter = options.get("module")
        catalog = PERMISSIONS_CATALOG

        if module_filter:
            if module_filter not in catalog:
                self.stderr.write(
                    self.style.ERROR(
                        f"Module '{module_filter}' not found in catalog"
                    )
                )
                return
            catalog = {module_filter: catalog[module_filter]}

        created_count = 0
        existing_count = 0

        for module, perms in catalog.items():
            for codename, description in perms:
                _, created = Permission.objects.get_or_create(
                    codename=codename,
                    defaults={"description": description, "module": module},
                )
                if created:
                    created_count += 1
                else:
                    existing_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Permissions seed complete: {created_count} created, "
                f"{existing_count} already existed"
            )
        )
