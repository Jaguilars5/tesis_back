from django.core.management.base import BaseCommand

from apps.iam.models import Permission
from apps.core.constants.permissions import (
    academic,
    iam,
    people,
    analytics,
    grading,
    institutions,
    students,
    attendance,
    behavior,
    integration,
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
        ("iam", iam),
        ("people", people),
        ("institutions", institutions),
        ("academic", academic),
        ("students", students),
        ("grading", grading),
        ("analytics", analytics),
        ("attendance", attendance),
        ("behavior", behavior),
        ("integration", integration),
    ]
    for module_name, perms in modules:
        collected = _collect_permissions_from_dataclass(perms, module_name)

        description_overrides = {
            "iam.view_user": "Ver usuarios",
            "iam.create_user": "Crear usuarios",
            "iam.update_user": "Actualizar usuarios",
            "iam.delete_user": "Eliminar usuarios",
            "iam.view_role": "Ver roles",
            "iam.create_role": "Crear roles",
            "iam.update_role": "Actualizar roles",
            "iam.delete_role": "Eliminar roles",
            "iam.view_permission": "Ver permisos",
            "iam.create_permission": "Crear permisos",
            "iam.update_permission": "Actualizar permisos",
            "iam.delete_permission": "Eliminar permisos",
            "institutions.view_school_year": "Ver años escolares",
            "institutions.create_school_year": "Crear años escolares",
            "institutions.update_school_year": "Actualizar años escolares",
            "institutions.delete_school_year": "Eliminar años escolares",
            "people.view_person": "Ver personas",
            "people.create_person": "Crear personas",
            "people.update_person": "Actualizar personas",
            "people.delete_person": "Eliminar personas",
            "people.view_document_type": "Ver tipos de documento",
            "people.create_document_type": "Crear tipos de documento",
            "people.view_city": "Ver ciudades",
            "people.update_document_type": "Actualizar tipos de documento",
            "people.delete_document_type": "Eliminar tipos de documento",
            "institutions.view_section": "Ver secciones",
            "institutions.create_section": "Crear secciones",
            "institutions.update_section": "Actualizar secciones",
            "institutions.delete_section": "Eliminar secciones",
            "institutions.view_academic_level": "Ver niveles académicos",
            "institutions.create_academic_level": "Crear niveles académicos",
            "institutions.update_academic_level": "Actualizar niveles académicos",
            "institutions.delete_academic_level": "Eliminar niveles académicos",
            "institutions.view_academic_grade": "Ver grados académicos",
            "institutions.create_academic_grade": "Crear grados académicos",
            "institutions.update_academic_grade": "Actualizar grados académicos",
            "institutions.delete_academic_grade": "Eliminar grados académicos",
            "institutions.view_academic_sublevel": "Ver sublevels académicos",
            "institutions.create_academic_sublevel": "Crear sublevels académicos",
            "institutions.update_academic_sublevel": "Actualizar sublevels académicos",
            "institutions.delete_academic_sublevel": "Eliminar sublevels académicos",
            "academic.view_subject": "Ver materias",
            "academic.create_subject": "Crear materias",
            "academic.update_subject": "Actualizar materias",
            "academic.delete_subject": "Eliminar materias",
            "academic.view_period": "Ver períodos académicos",
            "academic.create_period": "Crear períodos académicos",
            "academic.update_period": "Actualizar períodos académicos",
            "academic.delete_period": "Eliminar períodos académicos",
            "academic.view_period_type": "Ver tipos de período",
            "academic.create_period_type": "Crear tipos de período",
            "academic.update_period_type": "Actualizar tipos de período",
            "academic.delete_period_type": "Eliminar tipos de período",
            "academic.view_teacher_subject": "Ver asignaciones docente-materia",
            "academic.create_teacher_subject": "Crear asignaciones docente-materia",
            "academic.update_teacher_subject": "Actualizar asignaciones docente-materia",
            "academic.delete_teacher_subject": "Eliminar asignaciones docente-materia",
            "students.view_student": "Ver estudiantes",
            "students.create_student": "Crear estudiantes",
            "students.update_student": "Actualizar estudiantes",
            "students.delete_student": "Eliminar estudiantes",
            "students.view_representative_relationship": "Ver relaciones estudiante-representante",
            "students.create_representative_relationship": "Crear relaciones estudiante-representante",
            "students.update_representative_relationship": "Actualizar relaciones estudiante-representante",
            "students.delete_representative_relationship": "Eliminar relaciones estudiante-representante",
            "grading.view_note": "Ver calificaciones",
            "grading.create_note": "Crear calificaciones",
            "grading.update_note": "Actualizar calificaciones",
            "grading.delete_note": "Eliminar calificaciones",
            "grading.view_qualitative_scale": "Ver escalas cualitativas",
            "grading.view_evaluation_block": "Ver bloques de evaluación",
            "grading.create_evaluation_block": "Crear bloques de evaluación",
            "grading.update_evaluation_block": "Actualizar bloques de evaluación",
            "grading.delete_evaluation_block": "Eliminar bloques de evaluación",
            "grading.view_block_component": "Ver componentes de bloque",
            "grading.create_block_component": "Crear componentes de bloque",
            "grading.update_block_component": "Actualizar componentes de bloque",
            "grading.delete_block_component": "Eliminar componentes de bloque",
            "grading.view_evaluative_activity": "Ver actividades evaluativas",
            "grading.create_evaluative_activity": "Crear actividades evaluativas",
            "grading.update_evaluative_activity": "Actualizar actividades evaluativas",
            "grading.delete_evaluative_activity": "Eliminar actividades evaluativas",
            "grading.view_grade_history": "Ver historial de cambios de nota",
            "analytics.view_risk_score": "Ver puntajes de riesgo",
            "analytics.view_feature_snapshot": "Ver snapshots de características",
            "analytics.view_risk_factor": "Ver factores de riesgo",
            "analytics.view_student_risk_factor": "Ver factores de riesgo del estudiante",
            "analytics.create_student_risk_factor": "Crear factores de riesgo del estudiante",
            "students.view_enrollment": "Ver matrículas",
            "students.create_enrollment": "Crear matrículas",
            "students.update_enrollment": "Actualizar matrículas",
            "students.delete_enrollment": "Eliminar matrículas",
            "students.withdraw_student": "Retirar estudiante",
            "students.transfer_student": "Transferir estudiante",
            "students.view_kinship": "Ver tipos de parentesco",
            "students.view_special_needs_type": "Ver tipos de NEE",
            "academic.view_subject_config": "Ver configuraciones de materia",
            "academic.create_subject_config": "Crear configuraciones de materia",
            "academic.update_subject_config": "Actualizar configuraciones de materia",
            "academic.delete_subject_config": "Eliminar configuraciones de materia",
            "academic.view_subject_offering": "Ver ofertas de materia",
            "academic.create_subject_offering": "Crear ofertas de materia",
            "academic.update_subject_offering": "Actualizar ofertas de materia",
            "academic.delete_subject_offering": "Eliminar ofertas de materia",
            "academic.view_class_schedule": "Ver horarios de clase",
            "academic.create_class_schedule": "Crear horarios de clase",
            "academic.update_class_schedule": "Actualizar horarios de clase",
            "academic.delete_class_schedule": "Eliminar horarios de clase",
            "grading.view_grade_summary": "Ver resúmenes de calificaciones",
            "grading.create_grade_summary": "Crear resúmenes de calificaciones",
            "grading.update_grade_summary": "Actualizar resúmenes de calificaciones",
            "grading.delete_grade_summary": "Eliminar resúmenes de calificaciones",
            "grading.recalculate_grade_summary": "Recalcular resúmenes de calificaciones",

            "grading.create_qualitative_scale": "Crear escalas cualitativas",
            "grading.update_qualitative_scale": "Actualizar escalas cualitativas",
            "grading.delete_qualitative_scale": "Eliminar escalas cualitativas",
            "grading.view_activity_type": "Ver tipos de actividad",
            "grading.create_activity_type": "Crear tipos de actividad",
            "grading.update_activity_type": "Actualizar tipos de actividad",
            "grading.delete_activity_type": "Eliminar tipos de actividad",

            "analytics.view_early_alert": "Ver alertas tempranas",
            "analytics.create_early_alert": "Crear alertas tempranas",
            "analytics.update_early_alert": "Actualizar alertas tempranas",
            "analytics.delete_early_alert": "Eliminar alertas tempranas",
            "analytics.view_scoring_config": "Ver configuración del motor de riesgo",
            "analytics.update_scoring_config": "Actualizar configuración del motor de riesgo",
            "attendance.view_attendance": "Ver registros de asistencia",
            "attendance.create_attendance": "Crear registros de asistencia",
            "attendance.update_attendance": "Actualizar registros de asistencia",
            "attendance.delete_attendance": "Eliminar registros de asistencia",
            "behavior.view_conduct_incident": "Ver incidentes de conducta",
            "behavior.create_conduct_incident": "Crear incidentes de conducta",
            "behavior.update_conduct_incident": "Actualizar incidentes de conducta",
            "behavior.delete_conduct_incident": "Eliminar incidentes de conducta",
            "behavior.view_behavior_evaluation": "Ver evaluaciones de comportamiento",
            "behavior.create_behavior_evaluation": "Crear evaluaciones de comportamiento",
            "behavior.update_behavior_evaluation": "Actualizar evaluaciones de comportamiento",
            "behavior.delete_behavior_evaluation": "Eliminar evaluaciones de comportamiento",
            "behavior.view_incident_type": "Ver tipos de incidente",
            "behavior.create_incident_type": "Crear tipos de incidente",
            "behavior.update_incident_type": "Actualizar tipos de incidente",
            "behavior.delete_incident_type": "Eliminar tipos de incidente",
            "behavior.view_severity": "Ver severidades",
            "behavior.create_severity": "Crear severidades",
            "behavior.update_severity": "Actualizar severidades",
            "behavior.delete_severity": "Eliminar severidades",
            "integration.view_syncqueue": "Ver cola de sincronización",
            "integration.create_syncqueue": "Crear cola de sincronización",
            "integration.update_syncqueue": "Actualizar cola de sincronización",
            "integration.delete_syncqueue": "Eliminar cola de sincronización",
        }
        result = []
        for code, desc in collected:
            result.append((code, description_overrides.get(code, desc)))
        catalog[module_name] = result
    return catalog


PERMISSIONS_CATALOG = _build_catalog()


ROLES_CONFIG = {
    "ESTUDIANTE": {
        "name": "Estudiante",
        "description": "Rol de Estudiante",
        "permissions": [
            "academic.view_period",
            "academic.view_period_type",
            "academic.view_subject",
            "institutions.view_section",
            "academic.view_subject_offering",
            "institutions.view_academic_level",
            "institutions.view_academic_grade",
            "grading.view_note",
            "grading.view_qualitative_scale",
            "grading.view_activity_type",
            "grading.view_evaluative_activity",
            "grading.view_grade_summary",
            "attendance.view_attendance",
            "attendance.view_attendance_status",
            "behavior.view_conduct_incident",
            "behavior.view_behavior_evaluation",
            "students.view_kinship",
            "students.view_enrollment",
        ],
    },
    "REPRESENTANTE": {
        "name": "Representante",
        "description": "Rol de Representante",
        "permissions": [
            "academic.view_period",
            "academic.view_period_type",
            "academic.view_subject",
            "institutions.view_section",
            "academic.view_subject_offering",
            "institutions.view_academic_level",
            "institutions.view_academic_grade",
            "grading.view_note",
            "grading.view_qualitative_scale",
            "grading.view_activity_type",
            "grading.view_evaluative_activity",
            "grading.view_grade_summary",
            "attendance.view_attendance",
            "attendance.view_attendance_status",
            "behavior.view_conduct_incident",
            "behavior.view_behavior_evaluation",
            "analytics.view_early_alert",
            "analytics.view_risk_score",
            "students.view_kinship",
        ],
    },
    "DOCENTE": {
        "name": "Docente",
        "description": "Rol de Docente",
        "permissions": [
            "academic.view_period",
            "academic.view_period_type",
            "institutions.view_section",
            "academic.view_subject_offering",
            "institutions.view_academic_level",
            "institutions.view_academic_grade",
            "institutions.view_school_year",
            "academic.view_subject",
            "iam.view_user",
            "academic.view_teacher_subject",
            "academic.view_class_schedule",
            "grading.view_note",
            "grading.create_note",
            "grading.update_note",
            "grading.view_qualitative_scale",
            "grading.view_activity_type",
            "grading.view_block_component",
            "grading.view_evaluative_activity",
            "grading.create_evaluative_activity",
            "grading.update_evaluative_activity",
            "grading.view_grade_summary",
            "grading.create_grade_summary",
            "grading.update_grade_summary",
            "grading.view_grade_history",
            "attendance.view_attendance",
            "attendance.create_attendance",
            "attendance.update_attendance",
            "attendance.view_attendance_status",
            "attendance.view_absence_type",
            "behavior.view_conduct_incident",
            "behavior.create_conduct_incident",
            "behavior.update_conduct_incident",
            "behavior.view_incident_type",
            "behavior.view_severity",
            "analytics.view_early_alert",
            "analytics.view_risk_score",
            "students.view_student",
            "students.view_kinship",
            "students.view_enrollment",
        ],
    },
    "DIRECTOR": {
        "name": "Director",
        "description": "Rol de Director",
        "permissions": [
            "academic.view_period",
            "academic.create_period",
            "academic.update_period",
            "academic.delete_period",
            "academic.view_period_type",
            "academic.create_period_type",
            "academic.update_period_type",
            "academic.delete_period_type",
            "academic.view_subject",
            "academic.create_subject",
            "academic.update_subject",
            "academic.delete_subject",
            "academic.view_class_schedule",
            "academic.create_class_schedule",
            "academic.update_class_schedule",
            "academic.delete_class_schedule",
            "institutions.view_section",
            "institutions.create_section",
            "institutions.update_section",
            "institutions.delete_section",
            "academic.view_subject_offering",
            "academic.create_subject_offering",
            "academic.update_subject_offering",
            "academic.delete_subject_offering",
            "institutions.view_academic_level",
            "institutions.create_academic_level",
            "institutions.update_academic_level",
            "institutions.delete_academic_level",
            "institutions.view_academic_sublevel",
            "institutions.create_academic_sublevel",
            "institutions.update_academic_sublevel",
            "institutions.delete_academic_sublevel",
            "institutions.view_academic_grade",
            "institutions.create_academic_grade",
            "institutions.update_academic_grade",
            "institutions.delete_academic_grade",
            "institutions.view_school_year",
            "institutions.create_school_year",
            "institutions.update_school_year",
            "institutions.delete_school_year",
            "academic.view_subject_config",
            "academic.create_subject_config",
            "academic.update_subject_config",
            "academic.delete_subject_config",
            "academic.view_teacher_subject",
            "academic.create_teacher_subject",
            "academic.update_teacher_subject",
            "academic.delete_teacher_subject",
            "iam.view_user",
            "iam.create_user",
            "iam.update_user",
            "iam.delete_user",
            "iam.view_role",
            "iam.create_role",
            "iam.update_role",
            "iam.delete_role",
            "iam.view_permission",
            "iam.create_permission",
            "iam.update_permission",
            "iam.delete_permission",
            "people.view_person",
            "people.create_person",
            "people.update_person",
            "people.delete_person",
            "people.view_document_type",
            "people.create_document_type",
            "people.update_document_type",
            "people.delete_document_type",
            "students.view_enrollment",
            "students.create_enrollment",
            "students.update_enrollment",
            "students.delete_enrollment",
            "students.view_student",
            "students.create_student",
            "students.update_student",
            "students.delete_student",
            "students.view_representative_relationship",
            "students.create_representative_relationship",
            "students.update_representative_relationship",
            "students.delete_representative_relationship",
            "students.withdraw_student",
            "students.transfer_student",
            "students.view_kinship",
            "grading.view_note",
            "grading.view_qualitative_scale",
            "grading.create_qualitative_scale",
            "grading.update_qualitative_scale",
            "grading.delete_qualitative_scale",
            "grading.view_activity_type",
            "grading.create_activity_type",
            "grading.update_activity_type",
            "grading.delete_activity_type",
            "grading.view_evaluation_block",
            "grading.create_evaluation_block",
            "grading.update_evaluation_block",
            "grading.delete_evaluation_block",
            "grading.view_block_component",
            "grading.create_block_component",
            "grading.update_block_component",
            "grading.delete_block_component",
            "grading.view_evaluative_activity",
            "grading.view_grade_summary",
            "grading.create_grade_summary",
            "grading.update_grade_summary",
            "grading.delete_grade_summary",
            "grading.view_grade_history",
            "attendance.view_attendance",
            "attendance.view_attendance_status",
            "attendance.create_attendance_status",
            "attendance.update_attendance_status",
            "attendance.delete_attendance_status",
            "attendance.view_absence_type",
            "attendance.create_absence_type",
            "attendance.update_absence_type",
            "attendance.delete_absence_type",
            "behavior.view_conduct_incident",
            "behavior.create_conduct_incident",
            "behavior.update_conduct_incident",
            "behavior.delete_conduct_incident",
            "behavior.view_behavior_evaluation",
            "behavior.create_behavior_evaluation",
            "behavior.update_behavior_evaluation",
            "behavior.delete_behavior_evaluation",
            "behavior.view_incident_type",
            "behavior.create_incident_type",
            "behavior.update_incident_type",
            "behavior.delete_incident_type",
            "behavior.view_severity",
            "analytics.view_risk_score",
            "analytics.view_feature_snapshot",
            "analytics.view_risk_factor",
            "analytics.view_student_risk_factor",
            "analytics.create_student_risk_factor",
            "analytics.update_student_risk_factor",
            "analytics.delete_student_risk_factor",
            "analytics.view_early_alert",
            "analytics.create_early_alert",
            "analytics.update_early_alert",
            "analytics.delete_early_alert",
            "analytics.view_scoring_config",
            "analytics.update_scoring_config",
            "integration.view_syncqueue",
            "integration.create_syncqueue",
            "integration.update_syncqueue",
            "integration.delete_syncqueue",
        ],
    },
    "RECTOR": {
        "name": "Rector",
        "description": "Rol de Rector",
        "permissions": [
            "academic.view_period",
            "academic.view_period_type",
            "academic.view_subject",
            "institutions.view_section",
            "institutions.view_school_year",
            "institutions.view_academic_level",
            "institutions.view_academic_grade",
            "academic.view_subject_offering",
            "academic.view_class_schedule",
            "grading.view_grade_summary",
            "grading.view_grade_history",
            "grading.view_evaluative_activity",
            "grading.view_note",
            "grading.view_qualitative_scale",
            "behavior.view_conduct_incident",
            "behavior.view_behavior_evaluation",
            "behavior.view_incident_type",
            "behavior.view_severity",
            "attendance.view_attendance",
            "attendance.view_attendance_status",
            "attendance.view_absence_type",
            "analytics.view_risk_score",
            "analytics.view_feature_snapshot",
            "analytics.view_early_alert",
            "analytics.view_scoring_config",
            "analytics.view_student_risk_factor",
            "students.view_student",
            "students.view_enrollment",
            "students.view_kinship",
        ],
    },
    "CONSEJERO": {
        "name": "Consejero/DECE",
        "description": "Rol de Consejero/DECE",
        "permissions": [
            "academic.view_period",
            "academic.view_period_type",
            "academic.view_subject",
            "institutions.view_section",
            "academic.view_subject_offering",
            "institutions.view_academic_level",
            "institutions.view_academic_grade",
            "iam.view_user",
            "students.view_student",
            "students.view_representative_relationship",
            "students.view_enrollment",
            "students.view_kinship",
            "behavior.view_conduct_incident",
            "behavior.create_conduct_incident",
            "behavior.update_conduct_incident",
            "behavior.view_behavior_evaluation",
            "behavior.create_behavior_evaluation",
            "behavior.update_behavior_evaluation",
            "behavior.view_incident_type",
            "behavior.view_severity",
            "analytics.view_early_alert",
            "analytics.create_early_alert",
            "analytics.update_early_alert",
            "analytics.delete_early_alert",
            "analytics.view_risk_score",
            "analytics.view_student_risk_factor",
            "analytics.create_student_risk_factor",
            "analytics.update_student_risk_factor",
        ],
    },
}


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
                    self.style.ERROR(f"Module '{module_filter}' not found in catalog")
                )
                return
            catalog = {module_filter: catalog[module_filter]}

        created_count = 0
        existing_count = 0

        for module, perms in catalog.items():
            for code, description in perms:
                _, created = Permission.objects.get_or_create(
                    code=code,
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

        if not module_filter:
            from apps.iam.models import Role, RolePermission

            self.stdout.write("Seeding roles and their associated permissions...")
            for role_code, config in ROLES_CONFIG.items():
                role, created = Role.objects.get_or_create(
                    code=role_code,
                    defaults={
                        "name": config["name"],
                        "description": config["description"],
                        "is_active": True,
                    },
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"Created role: {role.name} ({role_code})")
                    )
                else:
                    role.name = config["name"]
                    role.description = config["description"]
                    role.save()

                RolePermission.objects.filter(role=role).delete()

                associations = []
                for perm_code in config["permissions"]:
                    try:
                        perm_obj = Permission.objects.get(code=perm_code)
                        associations.append(
                            RolePermission(role=role, permission=perm_obj)
                        )
                    except Permission.DoesNotExist:
                        self.stderr.write(
                            self.style.WARNING(
                                f"Permission '{perm_code}' not found in database. Skipping association with {role.name}."
                            )
                        )

                if associations:
                    RolePermission.objects.bulk_create(associations)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Associated {len(associations)} permissions to role {role.name}."
                        )
                    )
