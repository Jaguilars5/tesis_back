from django.core.management.base import BaseCommand

from apps.accounts.models import Permission
from apps.core.constants.permissions import (
    academic,
    accounts,
    analytics,
    grading,
    institutions,
    students,
    attendance,
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
        ("analytics", analytics),
        ("attendance", attendance),
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
            "accounts.view_person": "Ver personas",
            "accounts.create_person": "Crear personas",
            "accounts.update_person": "Actualizar personas",
            "accounts.delete_person": "Eliminar personas",
            "institutions.view_school_year": "Ver a\u00f1os escolares",
            "institutions.create_school_year": "Crear a\u00f1os escolares",
            "institutions.update_school_year": "Actualizar a\u00f1os escolares",
            "institutions.delete_school_year": "Eliminar a\u00f1os escolares",
            "institutions.view_document_type": "Ver tipos de documento",
            # Section (modelo en institutions)
            "institutions.view_section": "Ver secciones",
            "institutions.create_section": "Crear secciones",
            "institutions.update_section": "Actualizar secciones",
            "institutions.delete_section": "Eliminar secciones",
            # Academic Levels (módulo institutions)
            "institutions.view_academic_level": "Ver niveles acad\u00e9micos",
            "institutions.create_academic_level": "Crear niveles acad\u00e9micos",
            "institutions.update_academic_level": "Actualizar niveles acad\u00e9micos",
            "institutions.delete_academic_level": "Eliminar niveles acad\u00e9micos",
            # Academic Grades (módulo institutions)
            "institutions.view_academic_grade": "Ver grados acad\u00e9micos",
            "institutions.create_academic_grade": "Crear grados acad\u00e9micos",
            "institutions.update_academic_grade": "Actualizar grados acad\u00e9micos",
            "institutions.delete_academic_grade": "Eliminar grados acad\u00e9micos",
            "academic.view_subject": "Ver materias",
            "academic.create_subject": "Crear materias",
            "academic.update_subject": "Actualizar materias",
            "academic.delete_subject": "Eliminar materias",
            "academic.view_period": "Ver per\u00edodos acad\u00e9micos",
            "academic.create_period": "Crear per\u00edodos acad\u00e9micos",
            "academic.update_period": "Actualizar per\u00edodos acad\u00e9micos",
            "academic.delete_period": "Eliminar per\u00edodos acad\u00e9micos",
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
            "students.view_enrollment_status": "Ver estados de matr\u00edcula",
            "grading.view_note": "Ver calificaciones",
            "grading.create_note": "Crear calificaciones",
            "grading.update_note": "Actualizar calificaciones",
            "grading.delete_note": "Eliminar calificaciones",
            "grading.view_grade_type": "Ver tipos de nota",
            "grading.view_qualitative_scale": "Ver escalas cualitativas",
            "grading.view_evaluation_macro": "Ver macro evaluaciones",
            "grading.create_evaluation_macro": "Crear macro evaluaciones",
            "grading.update_evaluation_macro": "Actualizar macro evaluaciones",
            "grading.delete_evaluation_macro": "Eliminar macro evaluaciones",
            "grading.view_evaluation_criteria": "Ver criterios de evaluación",
            "grading.create_evaluation_criteria": "Crear criterios de evaluación",
            "grading.update_evaluation_criteria": "Actualizar criterios de evaluación",
            "grading.delete_evaluation_criteria": "Eliminar criterios de evaluación",
            "grading.view_evaluation_subcriteria": "Ver subcriterios de evaluación",
            "grading.create_evaluation_subcriteria": "Crear subcriterios de evaluación",
            "grading.update_evaluation_subcriteria": "Actualizar subcriterios de evaluación",
            "grading.delete_evaluation_subcriteria": "Eliminar subcriterios de evaluación",
            "grading.view_class_assignment": "Ver tareas/actividades",
            "grading.create_class_assignment": "Crear tareas/actividades",
            "grading.update_class_assignment": "Actualizar tareas/actividades",
            "grading.delete_class_assignment": "Eliminar tareas/actividades",
            "grading.view_grade_history": "Ver historial de cambios de nota",
            "analytics.view_risk_score": "Ver puntajes de riesgo",
            "analytics.view_feature_snapshot": "Ver snapshots de caracter\u00edsticas",
            "analytics.view_risk_factor": "Ver factores de riesgo",
            "analytics.view_student_risk_factor": "Ver factores de riesgo del estudiante",
            "analytics.create_student_risk_factor": "Crear factores de riesgo del estudiante",
            "analytics.delete_student_risk_factor": "Eliminar factores de riesgo del estudiante",
            "students.view_enrollment": "Ver matr\u00edculas",
            "students.create_enrollment": "Crear matr\u00edculas",
            "students.update_enrollment": "Actualizar matr\u00edculas",
            "students.delete_enrollment": "Eliminar matr\u00edculas",
            "students.enroll_student": "Matricular estudiante",
            "students.withdraw_student": "Retirar estudiante",
            "students.transfer_student": "Transferir estudiante",
            "academic.view_subject_config": "Ver configuraciones de materia",
            "academic.create_subject_config": "Crear configuraciones de materia",
            "academic.update_subject_config": "Actualizar configuraciones de materia",
            "academic.delete_subject_config": "Eliminar configuraciones de materia",
            "academic.view_subject_offering": "Ver ofertas de materia",
            "academic.create_subject_offering": "Crear ofertas de materia",
            "academic.update_subject_offering": "Actualizar ofertas de materia",
            "academic.delete_subject_offering": "Eliminar ofertas de materia",
            "grading.view_gradesummary": "Ver resúmenes de calificaciones",
            "grading.create_gradesummary": "Crear resúmenes de calificaciones",
            "grading.update_gradesummary": "Actualizar resúmenes de calificaciones",
            "grading.delete_gradesummary": "Eliminar resúmenes de calificaciones",
            "grading.view_recoveryprocess": "Ver procesos de recuperación",
            "grading.create_recoveryprocess": "Crear procesos de recuperación",
            "grading.update_recoveryprocess": "Actualizar procesos de recuperación",
            "grading.delete_recoveryprocess": "Eliminar procesos de recuperación",
            "grading.view_diagnosticevaluation": "Ver evaluaciones diagnósticas",
            "grading.create_diagnosticevaluation": "Crear evaluaciones diagnósticas",
            "grading.update_diagnosticevaluation": "Actualizar evaluaciones diagnósticas",
            "grading.delete_diagnosticevaluation": "Eliminar evaluaciones diagnósticas",
            "grading.view_projectnote": "Ver notas de proyectos",
            "grading.create_projectnote": "Crear notas de proyectos",
            "grading.update_projectnote": "Actualizar notas de proyectos",
            "grading.delete_projectnote": "Eliminar notas de proyectos",
            "analytics.view_earlyalert": "Ver alertas tempranas",
            "analytics.create_earlyalert": "Crear alertas tempranas",
            "analytics.update_earlyalert": "Actualizar alertas tempranas",
            "analytics.delete_earlyalert": "Eliminar alertas tempranas",
            "attendance.view_attendance": "Ver registros de asistencia",
            "attendance.create_attendance": "Crear registros de asistencia",
            "attendance.update_attendance": "Actualizar registros de asistencia",
            "attendance.delete_attendance": "Eliminar registros de asistencia",
            "attendance.view_conductincident": "Ver incidentes de conducta",
            "attendance.create_conductincident": "Crear incidentes de conducta",
            "attendance.update_conductincident": "Actualizar incidentes de conducta",
            "attendance.delete_conductincident": "Eliminar incidentes de conducta",
            "attendance.view_behaviorevaluation": "Ver evaluaciones de comportamiento",
            "attendance.create_behaviorevaluation": "Crear evaluaciones de comportamiento",
            "attendance.update_behaviorevaluation": "Actualizar evaluaciones de comportamiento",
            "attendance.delete_behaviorevaluation": "Eliminar evaluaciones de comportamiento",
            "attendance.view_incidenttype": "Ver tipos de incidente",
            "attendance.create_incidenttype": "Crear tipos de incidente",
            "attendance.update_incidenttype": "Actualizar tipos de incidente",
            "attendance.delete_incidenttype": "Eliminar tipos de incidente",
            "attendance.view_socioemotionalskill": "Ver habilidades socioemocionales",
            "attendance.create_socioemotionalskill": "Crear habilidades socioemocionales",
            "attendance.update_socioemotionalskill": "Actualizar habilidades socioemocionales",
            "attendance.delete_socioemotionalskill": "Eliminar habilidades socioemocionales",
            "attendance.view_skillevaluation": "Ver evaluaciones de habilidades",
            "attendance.create_skillevaluation": "Crear evaluaciones de habilidades",
            "attendance.update_skillevaluation": "Actualizar evaluaciones de habilidades",
            "attendance.delete_skillevaluation": "Eliminar evaluaciones de habilidades",
            "attendance.view_attendancestatus": "Ver estados de asistencia",
            "attendance.create_attendancestatus": "Crear estados de asistencia",
            "attendance.update_attendancestatus": "Actualizar estados de asistencia",
            "attendance.delete_attendancestatus": "Eliminar estados de asistencia",
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
            # dashboard
            "academic.view_period",
            "academic.view_subject",
            "institutions.view_section",
            "academic.view_subject_offering",
            "institutions.view_academic_level",
            "institutions.view_academic_grade",
            # grading (only view)
            "grading.view_note",
            "grading.view_grade_type",
            "grading.view_qualitative_scale",
            "grading.view_class_assignment",
            "grading.view_gradesummary",
            # attendance (only view)
            "attendance.view_attendance",
            "attendance.view_conductincident",
            "attendance.view_behaviorevaluation",
        ],
    },
    "REPRESENTANTE": {
        "name": "Representante",
        "description": "Rol de Representante",
        "permissions": [
            # dashboard
            "academic.view_period",
            "academic.view_subject",
            "institutions.view_section",
            "academic.view_subject_offering",
            "institutions.view_academic_level",
            "institutions.view_academic_grade",
            # grading (only view)
            "grading.view_note",
            "grading.view_grade_type",
            "grading.view_qualitative_scale",
            "grading.view_class_assignment",
            "grading.view_gradesummary",
            # attendance (only view)
            "attendance.view_attendance",
            # behavior (only view)
            "attendance.view_conductincident",
            "attendance.view_behaviorevaluation",
            "attendance.view_socioemotionalskill",
            "attendance.view_skillevaluation",
            # alerts
            "analytics.view_earlyalert",
            "analytics.view_risk_score",
        ],
    },
    "DOCENTE": {
        "name": "Docente",
        "description": "Rol de Docente",
        "permissions": [
            # dashboard
            "academic.view_period",
            "academic.view_subject",
            "institutions.view_section",
            "academic.view_subject_offering",
            "institutions.view_academic_level",
            "institutions.view_academic_grade",
            "academic.view_teacher_subject",
            # projects (all)
            "academic.view_config",
            "academic.create_config",
            "academic.update_config",
            "academic.delete_config",
            # grading (excluding structure, scales)
            # - register:
            "grading.view_note",
            "grading.create_note",
            "grading.update_note",
            "grading.delete_note",
            # - activities:
            "grading.view_class_assignment",
            "grading.create_class_assignment",
            "grading.update_class_assignment",
            "grading.delete_class_assignment",
            # - summaries:
            "grading.view_gradesummary",
            "grading.create_gradesummary",
            "grading.update_gradesummary",
            "grading.delete_gradesummary",
            # - recovery:
            "grading.view_recoveryprocess",
            "grading.create_recoveryprocess",
            "grading.update_recoveryprocess",
            "grading.delete_recoveryprocess",
            # - project note:
            "grading.view_projectnote",
            "grading.create_projectnote",
            "grading.update_projectnote",
            "grading.delete_projectnote",
            "grading.view_grade_history",
            # attendance (excluding states)
            # - daily:
            "attendance.view_attendance",
            "attendance.create_attendance",
            "attendance.update_attendance",
            "attendance.delete_attendance",
            # - behavior:
            "attendance.view_behaviorevaluation",
            "attendance.create_behaviorevaluation",
            "attendance.update_behaviorevaluation",
            "attendance.delete_behaviorevaluation",
            "attendance.view_conductincident",
            "attendance.create_conductincident",
            "attendance.update_conductincident",
            "attendance.delete_conductincident",
            # alerts (excluding risk-factors)
            # - early alerts:
            "analytics.view_earlyalert",
            "analytics.create_earlyalert",
            "analytics.update_earlyalert",
            "analytics.delete_earlyalert",
            # - risk score (view):
            "analytics.view_risk_score",
        ],
    },
    "DIRECTOR": {
        "name": "Director",
        "description": "Rol de Director",
        "permissions": [
            # dashboard & academic (full)
            "academic.view_period",
            "academic.create_period",
            "academic.update_period",
            "academic.delete_period",
            "academic.view_subject",
            "academic.create_subject",
            "academic.update_subject",
            "academic.delete_subject",
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
            "academic.view_config",
            "academic.create_config",
            "academic.update_config",
            "academic.delete_config",
            # people (excluding documents)
            "accounts.view_user",
            "accounts.create_user",
            "accounts.update_user",
            "accounts.delete_user",
            "accounts.view_person",
            "accounts.create_person",
            "accounts.update_person",
            "accounts.delete_person",
            "accounts.view_role",
            "accounts.create_role",
            "accounts.update_role",
            "accounts.delete_role",
            "accounts.view_permission",
            # enrollment (full)
            "students.view_enrollment",
            "students.create_enrollment",
            "students.update_enrollment",
            "students.delete_enrollment",
            "students.view_student",
            "students.create_student",
            "students.update_student",
            "students.delete_student",
            "students.view_representative",
            "students.create_representative",
            "students.update_representative",
            "students.delete_representative",
            "students.view_relationship",
            "students.create_relationship",
            "students.update_relationship",
            "students.delete_relationship",
            "students.view_enrollment_status",
            "students.enroll_student",
            "students.withdraw_student",
            "students.transfer_student",
            # grading (excluding register)
            "grading.view_grade_type",
            "grading.view_qualitative_scale",
            "grading.view_evaluation_macro",
            "grading.create_evaluation_macro",
            "grading.update_evaluation_macro",
            "grading.delete_evaluation_macro",
            "grading.view_evaluation_criteria",
            "grading.create_evaluation_criteria",
            "grading.update_evaluation_criteria",
            "grading.delete_evaluation_criteria",
            "grading.view_evaluation_subcriteria",
            "grading.create_evaluation_subcriteria",
            "grading.update_evaluation_subcriteria",
            "grading.delete_evaluation_subcriteria",
            "grading.view_class_assignment",
            "grading.create_class_assignment",
            "grading.update_class_assignment",
            "grading.delete_class_assignment",
            "grading.view_gradesummary",
            "grading.create_gradesummary",
            "grading.update_gradesummary",
            "grading.delete_gradesummary",
            "grading.view_recoveryprocess",
            "grading.create_recoveryprocess",
            "grading.update_recoveryprocess",
            "grading.delete_recoveryprocess",
            "grading.view_diagnosticevaluation",
            "grading.create_diagnosticevaluation",
            "grading.update_diagnosticevaluation",
            "grading.delete_diagnosticevaluation",
            "grading.view_projectnote",
            "grading.create_projectnote",
            "grading.update_projectnote",
            "grading.delete_projectnote",
            "grading.view_grade_history",
            # attendance (excluding behavior.skills)
            "attendance.view_attendance",
            "attendance.create_attendance",
            "attendance.update_attendance",
            "attendance.delete_attendance",
            "attendance.view_conductincident",
            "attendance.create_conductincident",
            "attendance.update_conductincident",
            "attendance.delete_conductincident",
            "attendance.view_behaviorevaluation",
            "attendance.create_behaviorevaluation",
            "attendance.update_behaviorevaluation",
            "attendance.delete_behaviorevaluation",
            "attendance.view_incidenttype",
            "attendance.create_incidenttype",
            "attendance.update_incidenttype",
            "attendance.delete_incidenttype",
            "attendance.view_attendancestatus",
            "attendance.create_attendancestatus",
            "attendance.update_attendancestatus",
            "attendance.delete_attendancestatus",
            # alerts & aibi
            "analytics.view_risk_score",
            "analytics.view_feature_snapshot",
            "analytics.view_risk_factor",
            "analytics.view_student_risk_factor",
            "analytics.create_student_risk_factor",
            "analytics.delete_student_risk_factor",
            "analytics.view_earlyalert",
            "analytics.create_earlyalert",
            "analytics.update_earlyalert",
            "analytics.delete_earlyalert",
        ],
    },
    "RECTOR": {
        "name": "Rector",
        "description": "Rol de Rector",
        "permissions": [
            # dashboard
            "academic.view_period",
            "academic.view_subject",
            "institutions.view_section",
            "academic.view_subject_offering",
            "institutions.view_academic_level",
            "institutions.view_academic_grade",
            # grading (excluding structure, activities, register, scales)
            "grading.view_gradesummary",
            "grading.view_recoveryprocess",
            "grading.view_diagnosticevaluation",
            "grading.view_projectnote",
            "grading.view_grade_history",
            # attendance (excluding daily, states)
            "attendance.view_conductincident",
            "attendance.view_behaviorevaluation",
            "attendance.view_incidenttype",
            "attendance.view_socioemotionalskill",
            "attendance.view_skillevaluation",
            # alerts & aibi (excluding new, risk-factors)
            "analytics.view_risk_score",
            "analytics.view_feature_snapshot",
        ],
    },
    "CONSEJERO": {
        "name": "Consejero/DECE",
        "description": "Rol de Consejero/DECE",
        "permissions": [
            # dashboard
            "academic.view_period",
            "academic.view_subject",
            "institutions.view_section",
            "academic.view_subject_offering",
            "institutions.view_academic_level",
            "institutions.view_academic_grade",
            # people
            "accounts.view_person",
            "accounts.view_user",
            "students.view_student",
            "students.view_representative",
            "students.view_relationship",
            # enrollment
            "students.view_enrollment",
            "students.view_enrollment_status",
            # behavior (skills, incidents, evaluations)
            "attendance.view_conductincident",
            "attendance.create_conductincident",
            "attendance.update_conductincident",
            "attendance.view_behaviorevaluation",
            "attendance.create_behaviorevaluation",
            "attendance.update_behaviorevaluation",
            "attendance.view_socioemotionalskill",
            "attendance.view_skillevaluation",
            "attendance.create_skillevaluation",
            "attendance.update_skillevaluation",
            # alerts (early alerts, risk scores, student risk factors)
            "analytics.view_earlyalert",
            "analytics.create_earlyalert",
            "analytics.update_earlyalert",
            "analytics.delete_earlyalert",
            "analytics.view_risk_score",
            "analytics.view_student_risk_factor",
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

        # Seed roles and their permissions if no module filter was applied (roles seed is global)
        if not module_filter:
            from apps.accounts.models import Role, RolePermission

            self.stdout.write("Seeding roles and their associated permissions...")
            for role_code, config in ROLES_CONFIG.items():
                role, created = Role.objects.get_or_create(
                    code=role_code,
                    defaults={
                        "name": config["name"],
                        "description": config["description"],
                        "active": True,
                    },
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"Created role: {role.name} ({role_code})")
                    )
                else:
                    # Update name/description if role already existed
                    role.name = config["name"]
                    role.description = config["description"]
                    role.save()

                # Clean up existing permissions for this role to avoid duplicates or orphaned permissions
                RolePermission.objects.filter(role=role).delete()

                # Associate permissions specified in the config
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
