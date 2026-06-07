import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.core.management import call_command

from apps.accounts.models import Person, User, Role, UserRole
from apps.academic.models import (
    Academic_Period,
    Subject,
    SubjectAcademicConfig,
    SubjectOffering,
    Teacher_Subject_Section,
)
from apps.grading.models import (
    BlockComponent,
    ComponentIndicator,
    EvaluationBlock,
    EvaluativeActivity,
)
from apps.institutions.models import (
    AcademicGrade,
    AcademicLevel,
    DocumentType,
    School_Year,
    Section,
)
from apps.students.models import (
    Enrollment,
    EnrollmentStatus,
    Student,
    Student_Representative,
)

DATA = {
    "school_year": {
        "name": "2024-2025",
        "start_date": datetime.date(2024, 9, 1),
        "end_date": datetime.date(2025, 6, 30),
        "active": True,
    },
    "academic_levels": [
        {"name": "Educación General Básica"},
        {"name": "Bachillerato General Unificado"},
    ],
    "academic_grades": [
        {
            "level_name": "Educación General Básica",
            "name": "7mo EGB",
            "subnivel": "MEDIA",
            "sequence_order": 7,
        },
        {
            "level_name": "Educación General Básica",
            "name": "8vo EGB",
            "subnivel": "SUPERIOR",
            "sequence_order": 8,
        },
        {
            "level_name": "Bachillerato General Unificado",
            "name": "1ro BGU",
            "subnivel": "BACHILLERATO",
            "sequence_order": 11,
        },
    ],
    "sections": [
        {"grade_name": "7mo EGB", "parallel": "A", "capacity": 30},
        {"grade_name": "7mo EGB", "parallel": "B", "capacity": 30},
        {"grade_name": "8vo EGB", "parallel": "A", "capacity": 30},
        {"grade_name": "1ro BGU", "parallel": "A", "capacity": 30},
    ],
    "subjects": [
        {"name": "Matemáticas", "code": "MAT-01"},
        {"name": "Lengua y Literatura", "code": "LYL-01"},
        {"name": "Ciencias Naturales", "code": "CCNN-01"},
        {"name": "Estudios Sociales", "code": "CCSS-01"},
        {"name": "Inglés", "code": "ING-01"},
    ],
    "subject_configs": [
        {
            "subject_code": "MAT-01",
            "grade_name": "7mo EGB",
            "weekly_hours": 5,
            "pedagogical_order": 1,
        },
        {
            "subject_code": "LYL-01",
            "grade_name": "7mo EGB",
            "weekly_hours": 5,
            "pedagogical_order": 2,
        },
        {
            "subject_code": "CCNN-01",
            "grade_name": "7mo EGB",
            "weekly_hours": 4,
            "pedagogical_order": 3,
        },
        {
            "subject_code": "CCSS-01",
            "grade_name": "7mo EGB",
            "weekly_hours": 4,
            "pedagogical_order": 4,
        },
        {
            "subject_code": "ING-01",
            "grade_name": "7mo EGB",
            "weekly_hours": 3,
            "pedagogical_order": 5,
        },
    ],
    "academic_periods": [
        {
            "name": "Quimestre 1",
            "period_type": "REGULAR",
            "start_date": datetime.date(2024, 9, 1),
            "end_date": datetime.date(2025, 1, 15),
        },
        {
            "name": "Quimestre 2",
            "period_type": "REGULAR",
            "start_date": datetime.date(2025, 1, 16),
            "end_date": datetime.date(2025, 6, 30),
        },
    ],
    "users": [
        {
            "tag": "admin",
            "document_number": "1000000001",
            "names": "Admin",
            "last_names": "Sistema",
            "email": "admin@test.com",
            "password": "test_Admin2024",
            "user_type": "ADMIN",
            "is_superuser": True,
            "role_code": None,
        },
        {
            "tag": "director",
            "document_number": "1000000002",
            "names": "Director",
            "last_names": "Académico",
            "email": "director@test.com",
            "password": "test_Director2024",
            "user_type": "DOCENTE",
            "is_superuser": False,
            "role_code": "DIRECTOR",
        },
        {
            "tag": "docente1",
            "document_number": "1000000003",
            "names": "Docente",
            "last_names": "Uno",
            "email": "docente1@test.com",
            "password": "test_Docente2024",
            "user_type": "DOCENTE",
            "is_superuser": False,
            "role_code": "DOCENTE",
        },
        {
            "tag": "docente2",
            "document_number": "1000000004",
            "names": "Docente",
            "last_names": "Dos",
            "email": "docente2@test.com",
            "password": "test_Docente2024",
            "user_type": "DOCENTE",
            "is_superuser": False,
            "role_code": "DOCENTE",
        },
        {
            "tag": "estudiante1",
            "document_number": "2000000001",
            "names": "Estudiante",
            "last_names": "Uno",
            "email": "estudiante1@test.com",
            "password": "test_Estudiante2024",
            "user_type": "ESTUDIANTE",
            "is_superuser": False,
            "role_code": "ESTUDIANTE",
        },
        {
            "tag": "estudiante2",
            "document_number": "2000000002",
            "names": "Estudiante",
            "last_names": "Dos",
            "email": "estudiante2@test.com",
            "password": "test_Estudiante2024",
            "user_type": "ESTUDIANTE",
            "is_superuser": False,
            "role_code": "ESTUDIANTE",
        },
        {
            "tag": "representante",
            "document_number": "1000000005",
            "names": "Representante",
            "last_names": "Familiar",
            "email": "representante@test.com",
            "password": "test_Representante2024",
            "user_type": "REPRESENTANTE",
            "is_superuser": False,
            "role_code": "REPRESENTANTE",
        },
        {
            "tag": "consejero",
            "document_number": "1000000006",
            "names": "Consejero",
            "last_names": "DECE",
            "email": "consejero@test.com",
            "password": "test_Consejero2024",
            "user_type": "DOCENTE",
            "is_superuser": False,
            "role_code": "CONSEJERO",
        },
    ],
}


class Command(BaseCommand):
    help = "Pobla la BD con datos de prueba (catálogos, roles, estructura institucional, usuarios)"

    def handle(self, *args, **options):
        self._seed_catalogs()
        self._seed_permissions_and_roles()
        school_year = self._create_school_year()
        levels = self._create_academic_levels()
        grades = self._create_academic_grades(levels)
        sections = self._create_sections(school_year, grades)
        subjects = self._create_subjects()
        subject_configs = self._create_subject_configs(subjects, grades)
        subject_offerings = self._create_subject_offerings(
            school_year, sections, subject_configs
        )
        periods = self._create_academic_periods(school_year)
        users = self._create_users()
        self._assign_roles(users)
        students = self._create_students(users)
        enrollments = self._create_enrollments(
            students, sections, school_year
        )
        self._create_representative_relationship(users, students)
        teacher_assignments = self._create_teacher_assignments(
            users, subject_offerings
        )
        grading_structure = self._create_grading_structure(periods)
        self._create_evaluative_activities(
            teacher_assignments, grading_structure
        )
        self._summary(
            school_year, levels, grades, sections, subjects,
            subject_configs, subject_offerings, periods, users,
            students, enrollments, teacher_assignments,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _seed_catalogs(self):
        self.stdout.write("  -> Sembrando catálogos...")
        call_command("seed_catalogs")

    def _seed_permissions_and_roles(self):
        self.stdout.write("  -> Sembrando permisos y roles...")
        call_command("seed_permissions")

    # ---- Institutional ----

    def _create_school_year(self):
        obj, _ = School_Year.objects.get_or_create(
            name=DATA["school_year"]["name"],
            defaults={
                "start_date": DATA["school_year"]["start_date"],
                "end_date": DATA["school_year"]["end_date"],
                "active": DATA["school_year"]["active"],
            },
        )
        self.stdout.write(f"  [OK] Año escolar: {obj.name}")
        return obj

    def _create_academic_levels(self):
        objs = []
        for item in DATA["academic_levels"]:
            obj, _ = AcademicLevel.objects.get_or_create(
                name=item["name"],
                defaults={"active": True},
            )
            objs.append(obj)
            self.stdout.write(f"  [OK] Nivel académico: {obj.name}")
        return objs

    def _create_academic_grades(self, levels):
        level_map = {l.name: l for l in levels}
        objs = {}
        for item in DATA["academic_grades"]:
            obj, _ = AcademicGrade.objects.get_or_create(
                name=item["name"],
                defaults={
                    "academic_level": level_map[item["level_name"]],
                    "subnivel": item["subnivel"],
                    "sequence_order": item["sequence_order"],
                    "active": True,
                },
            )
            objs[item["name"]] = obj
            self.stdout.write(f"  [OK] Grado: {obj.name} ({obj.subnivel})")
        return objs

    def _create_sections(self, school_year, grades):
        objs = {}
        for item in DATA["sections"]:
            grade = grades[item["grade_name"]]
            key = (item["grade_name"], item["parallel"])
            obj, _ = Section.objects.get_or_create(
                school_year=school_year,
                academic_grade=grade,
                parallel=item["parallel"],
                defaults={"capacity": item["capacity"], "active": True},
            )
            objs[key] = obj
            self.stdout.write(
                f"  [OK] Sección: {grade.name} {obj.parallel} "
                f"(cupo: {obj.capacity})"
            )
        return objs

    # ---- Academic ----

    def _create_subjects(self):
        objs = {}
        for item in DATA["subjects"]:
            obj, _ = Subject.objects.get_or_create(
                code=item["code"],
                defaults={"name": item["name"], "active": True},
            )
            objs[item["code"]] = obj
            self.stdout.write(f"  [OK] Materia: {obj.name} ({obj.code})")
        return objs

    def _create_subject_configs(self, subjects, grades):
        objs = {}
        for item in DATA["subject_configs"]:
            subj = subjects[item["subject_code"]]
            grade = grades[item["grade_name"]]
            obj, _ = SubjectAcademicConfig.objects.get_or_create(
                subject=subj,
                academic_grade=grade,
                defaults={
                    "weekly_hours": item["weekly_hours"],
                    "pedagogical_order": item["pedagogical_order"],
                    "is_required": True,
                    "active": True,
                },
            )
            key = (item["subject_code"], item["grade_name"])
            objs[key] = obj
            self.stdout.write(
                f"  [OK] Config materia: {subj.name} -> {grade.name} "
                f"({obj.weekly_hours}h/sem)"
            )
        return objs

    def _create_subject_offerings(self, school_year, sections, configs):
        objs = []
        for section_key, section in sections.items():
            grade_name = section_key[0]
            for cfg_key, cfg in configs.items():
                if cfg_key[1] != grade_name:
                    continue
                obj, _ = SubjectOffering.objects.get_or_create(
                    school_year=school_year,
                    section=section,
                    subject_academic_config=cfg,
                    defaults={"active": True},
                )
                objs.append(obj)
        self.stdout.write(f"  [OK] Ofertas de materia creadas: {len(objs)}")
        return objs

    def _create_academic_periods(self, school_year):
        objs = []
        for item in DATA["academic_periods"]:
            obj, _ = Academic_Period.objects.get_or_create(
                school_year=school_year,
                name=item["name"],
                defaults={
                    "period_type": item["period_type"],
                    "start_date": item["start_date"],
                    "end_date": item["end_date"],
                    "is_regular_period": True,
                },
            )
            objs.append(obj)
            self.stdout.write(f"  [OK] Período académico: {obj.name}")
        return objs

    # ---- Users ----

    def _create_users(self):
        doc_type = DocumentType.objects.get(code="CC")
        users = {}
        for item in DATA["users"]:
            person, _ = Person.objects.get_or_create(
                document_number=item["document_number"],
                defaults={
                    "document_type": doc_type,
                    "names": item["names"],
                    "last_names": item["last_names"],
                    "email": item["email"],
                    "active": True,
                },
            )
            if item["is_superuser"]:
                user, created = User.objects.get_or_create(
                    email=item["email"],
                    defaults={
                        "person": person,
                        "user_type": item["user_type"],
                        "is_staff": True,
                        "is_superuser": True,
                        "active": True,
                    },
                )
                if created:
                    user.set_password(item["password"])
                    user.save(update_fields=["password"])
            else:
                user, created = User.objects.get_or_create(
                    email=item["email"],
                    defaults={
                        "person": person,
                        "user_type": item["user_type"],
                        "active": True,
                    },
                )
                if created:
                    user.set_password(item["password"])
                    user.save(update_fields=["password"])
            users[item["tag"]] = user
            status = "creado" if created else "ya existente"
            self.stdout.write(
                f"  [OK] Usuario {item['tag']}: {item['email']} "
                f"({status})"
            )
        return users

    def _assign_roles(self, users):
        for item in DATA["users"]:
            role_code = item["role_code"]
            if not role_code:
                continue
            user = users[item["tag"]]
            role = Role.objects.get(code=role_code)
            _, created = UserRole.objects.get_or_create(
                user=user, role=role
            )
            status = "asignado" if created else "ya tiene"
            self.stdout.write(
                f"  [OK] Rol {role_code} -> {item['email']} ({status})"
            )

    # ---- Students ----

    def _create_students(self, users):
        students = {}
        for tag in ("estudiante1", "estudiante2"):
            user = users[tag]
            student, created = Student.objects.get_or_create(
                student_code=f"EST-{user.person.document_number}",
                defaults={
                    "person": user.person,
                    "active": True,
                },
            )
            students[tag] = student
            status = "creado" if created else "ya existe"
            self.stdout.write(
                f"  [OK] Estudiante: {student.get_full_name()} ({status})"
            )
        return students

    def _create_enrollments(self, students, sections, school_year):
        active_status = EnrollmentStatus.objects.get(code="ACT")
        enrollments = {}
        sections_list = list(sections.values())
        for idx, (tag, student) in enumerate(students.items()):
            section = sections_list[idx % len(sections_list)]
            enrollment, created = Enrollment.objects.get_or_create(
                student=student,
                section=section,
                school_year=school_year,
                defaults={
                    "enrollment_status": active_status,
                    "is_repeat": False,
                },
            )
            enrollments[tag] = enrollment
            status = "creada" if created else "ya existe"
            self.stdout.write(
                f"  [OK] Matrícula: {student.get_full_name()} -> "
                f"{section} ({status})"
            )
        return enrollments

    def _create_representative_relationship(self, users, students):
        rep_user = users["representante"]
        for tag in ("estudiante1", "estudiante2"):
            student = students[tag]
            _, created = Student_Representative.objects.get_or_create(
                student=student,
                person=rep_user.person,
                defaults={
                    "kinship": "Padre",
                    "is_primary": True,
                    "receives_notifications": True,
                },
            )
            status = "creada" if created else "ya existe"
            self.stdout.write(
                f"  [OK] Relación representante: "
                f"{rep_user.person.get_full_name()} -> "
                f"{student.get_full_name()} ({status})"
            )

    # ---- Teacher Assignment ----

    def _create_teacher_assignments(self, users, subject_offerings):
        teacher = users["docente1"]
        teacher2 = users["docente2"]
        assignments = []
        for offering in subject_offerings:
            t = teacher2 if "B" in str(offering.section.parallel) else teacher
            obj, created = Teacher_Subject_Section.objects.get_or_create(
                user=t,
                subject_offering=offering,
                defaults={"active": True},
            )
            if created:
                assignments.append(obj)
        if assignments:
            self.stdout.write(
                f"  [OK] Asignaciones docente-materia creadas: "
                f"{len(assignments)}"
            )
        return assignments or list(
            Teacher_Subject_Section.objects.filter(
                user__in=[teacher, teacher2]
            )
        )

    # ---- Grading Structure ----

    def _create_grading_structure(self, periods):
        result = {}
        for period in periods:
            block, _ = EvaluationBlock.objects.get_or_create(
                academic_period=period,
                evaluation_type="FORMATIVA",
                defaults={
                    "name": f"Formativa - {period.name}",
                    "weight_percentage": Decimal("100.00"),
                    "active": True,
                },
            )
            components_data = [
                ("Tareas", Decimal("40.00")),
                ("Lecciones", Decimal("30.00")),
                ("Talleres", Decimal("30.00")),
            ]
            comps = []
            for comp_name, weight in components_data:
                comp, _ = BlockComponent.objects.get_or_create(
                    evaluation_block=block,
                    name=comp_name,
                    defaults={"internal_weight": weight},
                )
                indicators_data = [
                    (f"Indicador 1 - {comp_name}", Decimal("50.00")),
                    (f"Indicador 2 - {comp_name}", Decimal("50.00")),
                ]
                inds = []
                for ind_name, ind_weight in indicators_data:
                    ind, _ = ComponentIndicator.objects.get_or_create(
                        block_component=comp,
                        name=ind_name,
                        defaults={"internal_weight": ind_weight},
                    )
                    inds.append(ind)
                comps.append({"component": comp, "indicators": inds})
            result[period.name] = {
                "block": block,
                "components": comps,
            }
            self.stdout.write(
                f"  [OK] Estructura de evaluación: {period.name}"
            )
        return result

    def _create_evaluative_activities(self, teacher_assignments, grading_structure):
        count = 0
        for period_name, structure in grading_structure.items():
            for comp in structure["components"]:
                for indicator in comp["indicators"]:
                    for tss in teacher_assignments[:2]:
                        _, created = EvaluativeActivity.objects.get_or_create(
                            component_indicator=indicator,
                            teacher_subject_section=tss,
                            title=f"Actividad - {indicator.name}",
                            defaults={
                                "activity_type": "TAREA",
                                "max_score": Decimal("10.00"),
                                "due_date": datetime.date(2024, 10, 15),
                            },
                        )
                        if created:
                            count += 1
        if count:
            self.stdout.write(
                f"  [OK] Actividades evaluativas creadas: {count}"
            )

    # ---- Summary ----

    def _summary(
        self, school_year, levels, grades, sections, subjects,
        configs, offerings, periods, users, students,
        enrollments, teacher_assignments,
    ):
        self.stdout.write(self.style.SUCCESS("\n" + "=" * 55))
        self.stdout.write(self.style.SUCCESS("  POBLACIÓN COMPLETADA"))
        self.stdout.write(self.style.SUCCESS("=" * 55))
        self.stdout.write(f"  Año escolar:       1")
        self.stdout.write(f"  Niveles:           {len(levels)}")
        self.stdout.write(f"  Grados:            {len(grades)}")
        self.stdout.write(f"  Secciones:         {len(sections)}")
        self.stdout.write(f"  Materias:          {len(subjects)}")
        self.stdout.write(f"  Configs materia:   {len(configs)}")
        self.stdout.write(f"  Ofertas materia:   {len(offerings)}")
        self.stdout.write(f"  Períodos académ:   {len(periods)}")
        self.stdout.write(f"  Usuarios creados:  {len(users)}")
        self.stdout.write(f"  Estudiantes:       {len(students)}")
        self.stdout.write(f"  Matrículas:        {len(enrollments)}")
        self.stdout.write(f"  Asignaciones doc:  {len(teacher_assignments)}")
        self.stdout.write(self.style.SUCCESS("-" * 55))
        self.stdout.write("  Credenciales de prueba:")
        for item in DATA["users"]:
            self.stdout.write(f"    • {item['email']} / {item['password']}")
        self.stdout.write(self.style.SUCCESS("=" * 55))
