# Correciones modelos

## Este documento presenta las correciones de los modelos, hay cambios bastante importantes

### People

- Tipo de documento

-- Actual

```py
class DocumentType(TimeStampedModel):
    code = models.CharField(max_length=10, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "people"
        db_table = "people_document_type"
        verbose_name = "Tipo de Documento"
        verbose_name_plural = "Tipos de Documento"
        ordering = ["name"]

    def __str__(self):
        return self.name

```

-- Corregido

```py
class DocumentType(TimeStampedModel):
    code = models.CharField(max_length=10, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "people"
        db_table = "people_document_type"
        verbose_name = "Tipo de Documento"
        verbose_name_plural = "Tipos de Documento"
        ordering = ["name"]

    def __str__(self):
        return self.name

```

- Persona (Person)

-- Actual

```py
class Person(TimeStampedModel):
    document_number = models.CharField(max_length=20, unique=True, verbose_name="Número de Documento")
    names = models.CharField(max_length=100, verbose_name="Nombres")
    last_names = models.CharField(max_length=100, verbose_name="Apellidos")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Fecha de Nacimiento")
    email = models.EmailField(blank=True, max_length=254, verbose_name="Correo Electrónico")
    phone = models.CharField(blank=True, max_length=15, verbose_name="Teléfono")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    document_type = models.ForeignKey(
        null=True, on_delete=PROTECT, to="people.documenttype", verbose_name="Tipo de Documento"
    )

    class Meta:
        verbose_name = "Persona"
        verbose_name_plural = "Personas"
        ordering = ["last_names", "names"]
        indexes = [
            Index(fields=["document_number"]),
            Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.names} {self.last_names}"

    def get_full_name(self):
        return f"{self.names} {self.last_names}"

    def get_age(self):
        if self.birth_date:
            today = timezone.now().date()
            age = today.year - self.birth_date.year
            if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
                age -= 1
            return age
        return None
```

-- Corregido

```py
class Person(TimeStampedModel):
    city = models.ForeignKey(
        "people.City",
        on_delete=models.PROTECT,
        verbose_name="Ciudad de Residencia",
    )
    document_type = models.ForeignKey(
        "people.DocumentType",
        on_delete=models.PROTECT,
        verbose_name="Tipo de Documento",
    )
    document_number = models.CharField(
        max_length=20, unique=True, verbose_name="Número de Documento"
    )
    birth_date = models.DateField(verbose_name="Fecha de Nacimiento")
    names = models.CharField(max_length=100, verbose_name="Nombres")
    last_names = models.CharField(max_length=100, verbose_name="Apellidos")
    email = models.EmailField(blank=True, verbose_name="Correo Electrónico")
    phone = models.CharField(max_length=15, blank=True, verbose_name="Teléfono")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "people"
        verbose_name = "Persona"
        verbose_name_plural = "Personas"
        ordering = ["last_names", "names"]
        indexes = [
            models.Index(fields=["document_number"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.names} {self.last_names}"

    def get_full_name(self):
        return f"{self.names} {self.last_names}"

    def get_age(self):
        if self.birth_date:
            today = timezone.now().date()
            age = today.year - self.birth_date.year
            if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
                age -= 1
            return age
        return None
```

- Ciudad (City)

-- Actual (NO existe en la migración, no se crea tabla)

```py
# No existe en apps/people/migrations/0001_initial.py
```

-- Corregido

```py
class City(TimeStampedModel):
    name = models.CharField(max_length=100, verbose_name="Nombre de la Ciudad")
    code = models.CharField(
        max_length=10, unique=True, verbose_name="Código de la Ciudad"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "people"
        db_table = "people_city"
        verbose_name = "Ciudad"
        verbose_name_plural = "Ciudades"
        ordering = ["name"]

    def __str__(self):
        return self.name
```

### Institutions

- Año Escolar (SchoolYear)

-- Actual

```py
class SchoolYear(TimeStampedModel):
    name = models.CharField(max_length=255, verbose_name="Nombre del Año Escolar")
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    end_date = models.DateField(verbose_name="Fecha de Fin")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Año Escolar"
        verbose_name_plural = "Años Escolares"

    def __str__(self):
        return self.name
```

-- Corregido

```py
class SchoolYear(TimeStampedModel):
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    end_date = models.DateField(verbose_name="Fecha de Fin")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "institutions"
        verbose_name = "Año Escolar"
        verbose_name_plural = "Años Escolares"

    def __str__(self):
        return f"{self.start_date} - {self.end_date}"
```

- Nivel Académico (AcademicLevel)

-- Actual

```py
class AcademicLevel(TimeStampedModel):
    code = models.CharField(blank=True, db_index=True, max_length=50, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre del Nivel")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Nivel Académico"
        verbose_name_plural = "Niveles Académicos"
        ordering = ["name"]

    def __str__(self):
        return self.name
```

-- Corregido

```py
class AcademicLevel(TimeStampedModel):
    name = models.CharField(max_length=100, verbose_name="Nombre del Nivel")
    code = models.CharField(
        max_length=50, blank=True, db_index=True, verbose_name="Código"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "institutions"
        verbose_name = "Nivel Académico"
        verbose_name_plural = "Niveles Académicos"
        ordering = ["name"]

    def __str__(self):
        return self.name
```

- Subnivel Académico (AcademicSublevel)

-- Actual

```py
class AcademicSublevel(TimeStampedModel):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    academic_level = models.ForeignKey(
        on_delete=CASCADE, related_name="sublevels", to="institutions.academiclevel", verbose_name="Nivel Académico"
    )

    class Meta:
        verbose_name = "Subnivel Académico"
        verbose_name_plural = "Subniveles Académicos"
        ordering = ["name"]
```

-- Corregido

```py
class AcademicSublevel(TimeStampedModel):
    academic_level = models.ForeignKey(
        "institutions.AcademicLevel",
        on_delete=models.CASCADE,
        verbose_name="Nivel Académico",
        related_name="sublevels",
    )
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "institutions"
        verbose_name = "Subnivel Académico"
        verbose_name_plural = "Subniveles Académicos"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"

    @property
    def academic_level_name(self):
        return self.academic_level.name if self.academic_level else None
```

- Grado Académico (AcademicGrade)

-- Actual

```py
class AcademicGrade(TimeStampedModel):
    code = models.CharField(blank=True, db_index=True, max_length=50, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre del Grado")
    sequence_order = models.IntegerField(verbose_name="Orden")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    academic_sublevel = models.ForeignKey(
        blank=True, null=True, on_delete=PROTECT, to="institutions.academicsublevel", verbose_name="Subnivel Académico"
    )

    class Meta:
        verbose_name = "Grado Académico"
        verbose_name_plural = "Grados Académicos"
        ordering = ["sequence_order"]
```

-- Corregido

```py
class AcademicGrade(TimeStampedModel):
    academic_sublevel = models.ForeignKey(
        "institutions.AcademicSublevel",
        on_delete=models.PROTECT,
        verbose_name="Subnivel Académico"
    )
    code = models.CharField(
        max_length=50, blank=True, db_index=True, verbose_name="Código"
    )
    name = models.CharField(max_length=100, verbose_name="Nombre del Grado")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "institutions"
        verbose_name = "Grado Académico"
        verbose_name_plural = "Grados Académicos"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"

    @property
    def academic_level(self):
        if self.academic_sublevel:
            return self.academic_sublevel.academic_level
        return None
```

- Sección (Section)

-- Actual

```py
class Section(TimeStampedModel):
    code = models.CharField(blank=True, db_index=True, max_length=50, verbose_name="Código")
    parallel = models.CharField(max_length=255, verbose_name="Paralelo")
    capacity = models.IntegerField(verbose_name="Capacidad")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    academic_grade = models.ForeignKey(
        null=True, on_delete=CASCADE, to="institutions.academicgrade", verbose_name="Grado Académico"
    )
    school_year = models.ForeignKey(
        on_delete=CASCADE, to="institutions.schoolyear", verbose_name="Año Escolar"
    )

    class Meta:
        verbose_name = "Sección"
        verbose_name_plural = "Secciones"
        unique_together = {("school_year", "academic_grade", "parallel")}
```

-- Corregido

```py
class Section(TimeStampedModel):
    school_year = models.ForeignKey(
        "institutions.SchoolYear",
        on_delete=models.CASCADE,
        verbose_name="Año Escolar",
    )
    academic_grade = models.ForeignKey(
        "institutions.AcademicGrade",
        on_delete=models.CASCADE,
        verbose_name="Grado Académico",
        null=True,
    )
    code = models.CharField(
        max_length=50, blank=True, db_index=True, verbose_name="Código"
    )
    parallel = models.CharField(max_length=255, verbose_name="Paralelo")
    capacity = models.IntegerField(verbose_name="Capacidad")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "institutions"
        verbose_name = "Sección"
        verbose_name_plural = "Secciones"
        unique_together = [("school_year", "academic_grade", "parallel")]

    def __str__(self):
        if self.academic_grade:
            return f"{self.academic_grade.name} {self.parallel}"
        return f"{self.parallel}"
```

### IAM

- Usuario (User)

-- Actual

```py
class User(AbstractBaseUser, TimeStampedModel):
    username = models.CharField(max_length=50, unique=True, verbose_name="Nombre de Usuario")
    email = models.EmailField(max_length=254, unique=True, verbose_name="Correo Electrónico")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    is_staff = models.BooleanField(default=False, verbose_name="Es Personal del Admin")
    is_superuser = models.BooleanField(default=False, verbose_name="Es Superusuario")
    person = models.OneToOneField(on_delete=CASCADE, to="people.person", verbose_name="Persona")

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["id"]
        indexes = [Index(fields=["is_active"])]
```

-- Corregido

```py
class User(AbstractBaseUser, TimeStampedModel):
    person = models.OneToOneField(
        "people.Person",
        on_delete=models.CASCADE,
        null=False,
        verbose_name="Persona",
    )
    username = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nombre de Usuario",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    is_staff = models.BooleanField(default=False, verbose_name="Es Personal del Admin")
    is_superuser = models.BooleanField(default=False, verbose_name="Es Superusuario")

    # Nota: El modelo no declara `email` explícitamente, lo deriva de person.email
```

### Academic

- Materia (Subject)

-- Actual

```py
class Subject(TimeStampedModel):
    name = models.CharField(max_length=255, verbose_name="Nombre de la Materia")
    code = models.CharField(max_length=100, unique=True, verbose_name="Código")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Materia"
        verbose_name_plural = "Materias"
```

-- Corregido

```py
class Subject(TimeStampedModel):
    name = models.CharField(max_length=255, verbose_name="Nombre de la Materia")
    code = models.CharField(max_length=100, unique=True, verbose_name="Código")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "academic"
        verbose_name = "Materia"
        verbose_name_plural = "Materias"
```

- Configuración de Materia por Grado (SubjectAcademicConfig)

-- Actual

```py
class SubjectAcademicConfig(TimeStampedModel):
    weekly_hours = models.IntegerField(verbose_name="Horas Semanales")
    pedagogical_order = models.IntegerField(verbose_name="Orden Pedagógico")
    is_required = models.BooleanField(default=True, verbose_name="Obligatoria")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    academic_grade = models.ForeignKey(
        on_delete=CASCADE, related_name="subject_academic_configs", to="institutions.academicgrade", verbose_name="Grado Académico"
    )
    subject = models.ForeignKey(
        on_delete=CASCADE, related_name="academic_configs", to="academic.subject", verbose_name="Materia"
    )

    class Meta:
        verbose_name = "Configuración de Materia por Grado"
        verbose_name_plural = "Configuraciones de Materia por Grado"
        ordering = ["pedagogical_order"]
        constraints = [UniqueConstraint(fields=["subject", "academic_grade"], name="unique_subject_academic_grade")]
```

-- Corregido

```py
class SubjectAcademicConfig(TimeStampedModel):
    academic_grade = models.ForeignKey(
        "institutions.AcademicGrade",
        on_delete=models.CASCADE,
        related_name="subject_academic_configs",
        verbose_name="Grado Académico",
    )
    subject = models.ForeignKey(
        "academic.Subject",
        on_delete=models.CASCADE,
        related_name="academic_configs",
        verbose_name="Materia",
    )
    weekly_hours = models.IntegerField(verbose_name="Horas Semanales")
    is_required = models.BooleanField(default=True, verbose_name="Obligatoria")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "academic"
        verbose_name = "Configuración de Materia por Grado"
        verbose_name_plural = "Configuraciones de Materia por Grado"
        ordering = ["subject"]
        constraints = [
            models.UniqueConstraint(
                fields=["subject", "academic_grade"],
                name="unique_subject_academic_grade",
            ),
        ]

    def __str__(self):
        return f"{self.subject.name} - {self.academic_grade.name}"
```

- Período Académico (AcademicPeriod)

-- Actual

```py
class AcademicPeriod(TimeStampedModel):
    code = models.CharField(blank=True, db_index=True, max_length=50, verbose_name="Código")
    name = models.CharField(max_length=80, verbose_name="Nombre del Período")
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    end_date = models.DateField(verbose_name="Fecha de Fin")
    year_weight = models.DecimalField(
        blank=True, decimal_places=2, max_digits=5, null=True,
        help_text="Porcentaje de contribución de este período a la nota anual (ej: 40.00 para Q1)",
        verbose_name="Peso en el año (%)",
    )
    is_regular_period = models.BooleanField(default=True, verbose_name="Período Regular")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    parent_period = models.ForeignKey(
        blank=True, null=True, on_delete=SET_NULL, related_name="child_periods",
        to="academic.academicperiod", verbose_name="Período Padre",
    )
    period_type = models.ForeignKey(
        default=_get_default_period_type, on_delete=PROTECT,
        to="academic.periodtype", verbose_name="Tipo de período",
    )
    school_year = models.ForeignKey(
        on_delete=CASCADE, related_name="academic_periods",
        to="institutions.schoolyear", verbose_name="Año Escolar",
    )

    class Meta:
        verbose_name = "Período Académico"
        verbose_name_plural = "Períodos Académicos"
```

-- Corregido

```py
class AcademicPeriod(TimeStampedModel):
    period_type = models.ForeignKey(
        "academic.PeriodType",
        on_delete=models.PROTECT,
        default=_get_default_period_type,
        verbose_name="Tipo de período",
    )
    school_year = models.ForeignKey(
        "institutions.SchoolYear",
        on_delete=models.CASCADE,
        related_name="academic_periods",
        verbose_name="Año Escolar",
    )
    code = models.CharField(
        max_length=50, blank=True, db_index=True, verbose_name="Código"
    )
    name = models.CharField(max_length=80, verbose_name="Nombre del Período")
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    end_date = models.DateField(verbose_name="Fecha de Fin")
    year_weight = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Peso en el año (%)",
        help_text="Porcentaje de contribución de este período a la nota anual (ej: 40.00 para Q1)",
    )
    is_regular_period = models.BooleanField(default=True, verbose_name="Período Regular")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
```

### Students

- Estudiante (Student)

-- Actual

```py
class Student(TimeStampedModel):
    student_code = models.CharField(max_length=50, unique=True, verbose_name="Código de Estudiante")
    distance_to_school_km = models.DecimalField(
        blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="Distancia al Colegio (km)"
    )
    has_special_needs = models.BooleanField(default=False, verbose_name="Tiene Necesidades Educativas Especiales (NEE)")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    person = models.OneToOneField(on_delete=CASCADE, to="people.person", verbose_name="Persona")
    residential_zone = models.ForeignKey(
        blank=True, null=True, on_delete=SET_NULL,
        to="students.residentialzone", verbose_name="Zona Residencial",
    )
    special_needs_type = models.ForeignKey(
        blank=True, null=True, on_delete=SET_NULL,
        to="students.specialneedstype", verbose_name="Tipo de NEE",
    )

    class Meta:
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"
        ordering = ["id"]
        indexes = [Index(fields=["student_code"])]
```

-- Corregido

```py
class Student(TimeStampedModel):
    user = models.OneToOneField(
        "iam.User",
        on_delete=models.CASCADE,
        null=False,
        verbose_name="Usuario",
    )
    special_needs_type = models.ForeignKey(
        "students.SpecialNeedsType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tipo de NEE",
    )
    student_code = models.CharField(
        max_length=50, unique=True, verbose_name="Código de Estudiante"
    )
    has_special_needs = models.BooleanField(
        default=False, verbose_name="Tiene Necesidades Educativas Especiales (NEE)"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "students"
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"
        ordering = ["id"]
        indexes = [
            models.Index(fields=["student_code"]),
        ]

    def __str__(self):
        if self.user:
            return self.user.get_full_name()
        return f"Student #{self.pk}"
```

- Representante (StudentRepresentative)

-- Actual

```py
class StudentRepresentative(TimeStampedModel):
    is_primary = models.BooleanField(default=False, verbose_name="Es Principal")
    can_pickup = models.BooleanField(default=True, verbose_name="Puede Recoger")
    emergency_contact = models.BooleanField(default=False, verbose_name="Contacto de Emergencia")
    receives_notifications = models.BooleanField(default=True, verbose_name="Recibe Notificaciones")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    kinship = models.ForeignKey(on_delete=PROTECT, to="students.kinship", verbose_name="Parentesco")
    person = models.ForeignKey(
        on_delete=CASCADE, related_name="student_representatives",
        to="people.person", verbose_name="Persona",
    )
    student = models.ForeignKey(
        on_delete=CASCADE, related_name="representatives_set",
        to="students.student", verbose_name="Estudiante",
    )

    class Meta:
        verbose_name = "Relación Estudiante-Representante"
        verbose_name_plural = "Relaciones Estudiante-Representante"
        ordering = ["-is_primary", "-created_at"]
        constraints = [
            UniqueConstraint(fields=["student", "person"], name="unique_student_person"),
            UniqueConstraint(
                fields=["student"], condition=Q(is_primary=True),
                name="unique_primary_representative_per_student",
            ),
        ]
```

-- Corregido

```py
class StudentRepresentative(TimeStampedModel):
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="representatives_set",
        verbose_name="Estudiante",
    )
    kinship = models.ForeignKey(
        "students.Kinship",
        on_delete=models.PROTECT,
        verbose_name="Parentesco",
    )
    user = models.ForeignKey(
        "iam.User",
        on_delete=models.CASCADE,
        related_name="student_representatives",
        null=False,
        verbose_name="Usuario del Representante",
    )
    is_primary = models.BooleanField(default=False, verbose_name="Es Principal")
    emergency_contact = models.BooleanField(
        default=False, verbose_name="Contacto de Emergencia"
    )
    receives_notifications = models.BooleanField(
        default=True, verbose_name="Recibe Notificaciones"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "students"
        verbose_name = "Relación Estudiante-Representante"
        verbose_name_plural = "Relaciones Estudiante-Representante"
        constraints = [
            UniqueConstraint(fields=["student", "user"], name="unique_student_user"),
            UniqueConstraint(
                fields=["student"],
                condition=models.Q(is_primary=True),
                name="unique_primary_representative_per_student",
            ),
        ]
        ordering = ["-is_primary", "-created_at"]
```

- Matrícula (Enrollment)

-- Actual

```py
class Enrollment(TimeStampedModel, SyncableModel):
    enrollment_status = models.CharField(
        max_length=5,
        choices=[("ACT","Activa"),("RET","Retirado"),("TRS","Transferido"),("SUS","Suspendido"),("GRA","Graduado")],
        verbose_name="Estado de Matrícula",
    )
    enrollment_date = models.DateField(auto_now_add=True, verbose_name="Fecha de Matrícula")
    withdrawal_date = models.DateField(blank=True, null=True, verbose_name="Fecha de Retiro")
    is_repeat = models.BooleanField(default=False, verbose_name="Es repitente")
    approved_by = models.ForeignKey(
        blank=True, null=True, on_delete=SET_NULL, related_name="enrollments_approved",
        to=AUTH_USER_MODEL, verbose_name="Aprobado por",
    )
    created_by = models.ForeignKey(
        blank=True, null=True, on_delete=SET_NULL, related_name="enrollments_created",
        to=AUTH_USER_MODEL, verbose_name="Creado por",
    )
    repeated_school_year = models.ForeignKey(
        blank=True, null=True, on_delete=SET_NULL, related_name="repeated_enrollments",
        to="institutions.schoolyear", verbose_name="Año escolar repetido",
    )
    section = models.ForeignKey(
        on_delete=CASCADE, related_name="enrollments",
        to="institutions.section", verbose_name="Sección",
    )
    student = models.ForeignKey(
        on_delete=CASCADE, related_name="enrollments",
        to="students.student", verbose_name="Estudiante",
    )
    withdrawal_reason = models.ForeignKey(
        blank=True, null=True, on_delete=SET_NULL,
        to="students.withdrawalreason", verbose_name="Motivo de Retiro",
    )

    class Meta:
        verbose_name = "Matrícula"
        verbose_name_plural = "Matrículas"
        constraints = [UniqueConstraint(fields=["student", "section"], name="unique_student_section")]
        indexes = [
            Index(fields=["student", "enrollment_status"]),
            Index(fields=["section", "enrollment_status"]),
        ]

    @property
    def school_year(self):
        return self.section.school_year
```

-- Corregido

```py
class Enrollment(TimeStampedModel, SyncableModel):
    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE,
        related_name="enrollments", verbose_name="Estudiante",
    )
    withdrawal_reason = models.ForeignKey(
        "students.WithdrawalReason", on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Motivo de Retiro",
    )
    section = models.ForeignKey(
        "institutions.Section", on_delete=models.CASCADE,
        related_name="enrollments", verbose_name="Sección",
    )
    enrollment_date = models.DateField(verbose_name="Fecha de Matrícula", auto_now_add=True)
    enrollment_status = models.CharField(
        max_length=5,
        choices=EnrollmentStatusChoices.choices,
        verbose_name="Estado de Matrícula",
    )
    withdrawal_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Retiro")
    is_repeat = models.BooleanField(default=False, verbose_name="Es repitente")

    class Meta:
        app_label = "students"
        verbose_name = "Matrícula"
        verbose_name_plural = "Matrículas"
        constraints = [
            UniqueConstraint(fields=["student", "section"], name="unique_student_section"),
        ]
        indexes = [
            models.Index(fields=["student", "enrollment_status"]),
            models.Index(fields=["section", "enrollment_status"]),
        ]

    @property
    def school_year(self):
        return self.section.school_year
```

### Attendance

- Asistencia (Attendance)

-- Actual

```py
class Attendance(TimeStampedModel, SyncableModel):
    attendance_date = models.DateField(verbose_name="Fecha")
    observation = models.TextField(blank=True, default="", verbose_name="Observaciones")
    absence_type = models.ForeignKey(
        blank=True, null=True, on_delete=SET_NULL,
        to="attendance.absencetype", verbose_name="Tipo de ausencia",
    )
    academic_period = models.ForeignKey(
        on_delete=CASCADE, related_name="attendance_records",
        to="academic.academicperiod", verbose_name="Período Académico",
    )
    attendance_status = models.ForeignKey(
        on_delete=PROTECT, to="attendance.attendancestatus", verbose_name="Estado",
    )
    created_by = models.ForeignKey(
        blank=True, null=True, on_delete=SET_NULL, related_name="attendances_created",
        to=AUTH_USER_MODEL, verbose_name="Creado por",
    )
    enrollment = models.ForeignKey(
        on_delete=CASCADE, related_name="attendance_records",
        to="students.enrollment", verbose_name="Matrícula",
    )
    modified_by = models.ForeignKey(
        blank=True, null=True, on_delete=SET_NULL, related_name="attendances_modified",
        to=AUTH_USER_MODEL, verbose_name="Modificado por",
    )
    teacher_subject_section = models.ForeignKey(
        on_delete=CASCADE, related_name="attendance_records",
        to="academic.teachersubjectsection", verbose_name="Clase",
    )

    class Meta:
        verbose_name = "Asistencia"
        verbose_name_plural = "Asistencias"
        unique_together = {("enrollment", "teacher_subject_section", "attendance_date")}
        indexes = [
            Index(fields=["enrollment", "academic_period"]),
            Index(fields=["teacher_subject_section", "attendance_date"]),
            Index(fields=["attendance_date", "academic_period"]),
        ]
```

-- Corregido

```py
class Attendance(TimeStampedModel, SyncableModel):
    absence_type = models.ForeignKey(
        "attendance.AbsenceType", on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Tipo de ausencia",
    )
    attendance_status = models.ForeignKey(
        "attendance.AttendanceStatus", on_delete=models.PROTECT, verbose_name="Estado",
    )
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod", on_delete=models.CASCADE,
        related_name="attendance_records", verbose_name="Período Académico",
    )
    enrollment = models.ForeignKey(
        "students.Enrollment", on_delete=models.CASCADE,
        related_name="attendance_records", verbose_name="Matrícula",
    )
    teacher_subject_section = models.ForeignKey(
        "academic.TeacherSubjectSection", on_delete=models.CASCADE,
        related_name="attendance_records", verbose_name="Clase",
    )
    attendance_date = models.DateField(verbose_name="Fecha")
    observation = models.TextField(blank=True, default="", verbose_name="Observaciones")

    class Meta:
        app_label = "attendance"
        verbose_name = "Asistencia"
        verbose_name_plural = "Asistencias"
        unique_together = ("enrollment", "teacher_subject_section", "attendance_date")
        indexes = [
            models.Index(fields=["enrollment", "academic_period"]),
            models.Index(fields=["teacher_subject_section", "attendance_date"]),
            models.Index(fields=["attendance_date", "academic_period"]),
        ]

    def clean(self):
        # validaciones cruzadas
        ...
```

### Behavior

- Severidad (Severity)

-- Actual

```py
class Severity(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    numeric_level = models.IntegerField(verbose_name="Nivel Numérico")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Severidad"
        verbose_name_plural = "Severidades"
        ordering = ["numeric_level"]
```

-- Corregido

```py
class Severity(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "behavior"
        verbose_name = "Severidad"
        verbose_name_plural = "Severidades"
        ordering = ["name"]
```

- Incidente de Conducta (ConductIncident)

-- Actual

```py
class ConductIncident(TimeStampedModel, SyncableModel):
    incident_date = models.DateField(verbose_name="Fecha del Incidente")
    description = models.TextField(blank=True, default="", verbose_name="Descripción")
    actions_taken = models.TextField(blank=True, default="", verbose_name="Acciones tomadas")
    family_notified = models.BooleanField(default=False, verbose_name="Familia Notificada")
    academic_period = models.ForeignKey(
        on_delete=CASCADE, related_name="conduct_incidents",
        to="academic.academicperiod", verbose_name="Período Académico",
    )
    approved_by = models.ForeignKey(
        blank=True, null=True, on_delete=SET_NULL, related_name="incidents_approved",
        to=AUTH_USER_MODEL, verbose_name="Aprobado por",
    )
    created_by = models.ForeignKey(
        blank=True, null=True, on_delete=SET_NULL, related_name="incidents_created",
        to=AUTH_USER_MODEL, verbose_name="Creado por",
    )
    enrollment = models.ForeignKey(
        on_delete=CASCADE, related_name="conduct_incidents",
        to="students.enrollment", verbose_name="Matrícula",
    )
    incident_type = models.ForeignKey(
        on_delete=PROTECT, to="behavior.incidenttype", verbose_name="Tipo de incidente",
    )
    modified_by = models.ForeignKey(
        blank=True, null=True, on_delete=SET_NULL, related_name="incidents_modified",
        to=AUTH_USER_MODEL, verbose_name="Modificado por",
    )
    reported_by_user = models.ForeignKey(
        null=True, on_delete=SET_NULL, related_name="reported_conduct_incidents",
        to=AUTH_USER_MODEL, verbose_name="Reportado por",
    )
    severity = models.ForeignKey(
        on_delete=PROTECT, to="behavior.severity", verbose_name="Severidad",
    )

    class Meta:
        verbose_name = "Incidente de Conducta"
        verbose_name_plural = "Incidentes de Conducta"
        ordering = ["-incident_date"]
        indexes = [
            Index(fields=["enrollment", "academic_period"]),
            Index(fields=["academic_period", "severity"]),
            Index(fields=["incident_date"]),
        ]
```

-- Corregido

```py
class ConductIncident(TimeStampedModel, SyncableModel):
    incident_type = models.ForeignKey(
        "behavior.IncidentType", on_delete=models.PROTECT, verbose_name="Tipo de incidente",
    )
    severity = models.ForeignKey(
        "behavior.Severity", on_delete=models.PROTECT, verbose_name="Severidad",
    )
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod", on_delete=models.CASCADE,
        related_name="conduct_incidents", verbose_name="Período Académico",
    )
    enrollment = models.ForeignKey(
        "students.Enrollment", on_delete=models.CASCADE,
        related_name="conduct_incidents", verbose_name="Matrícula",
    )
    incident_date = models.DateField(verbose_name="Fecha del Incidente")
    description = models.TextField(blank=True, default="", verbose_name="Descripción")
    actions_taken = models.TextField(blank=True, default="", verbose_name="Acciones tomadas")
    family_notified = models.BooleanField(default=False, verbose_name="Familia Notificada")

    class Meta:
        app_label = "behavior"
        verbose_name = "Incidente de Conducta"
        verbose_name_plural = "Incidentes de Conducta"
        ordering = ["-incident_date"]
        indexes = [
            models.Index(fields=["enrollment", "academic_period"]),
            models.Index(fields=["academic_period", "severity"]),
            models.Index(fields=["incident_date"]),
        ]
```

- Evaluación de Conducta (BehaviorEvaluation)

-- Actual

```py
class BehaviorEvaluation(TimeStampedModel, SyncableModel):
    general_observation = models.TextField(blank=True, default="", verbose_name="Observación general")
    override_reason = models.TextField(blank=True, default="", verbose_name="Razón de anulación")
    evaluation_date = models.DateField(default=date.today, verbose_name="Fecha de evaluación")
    approval_date = models.DateField(blank=True, null=True, verbose_name="Fecha de aprobación")
    academic_period = models.ForeignKey(
        on_delete=CASCADE, related_name="attendance_behavior_evaluations",
        to="academic.academicperiod", verbose_name="Período Académico",
    )
    approved_by = models.ForeignKey(
        blank=True, null=True, on_delete=SET_NULL, related_name="behavior_evaluations_approved",
        to=AUTH_USER_MODEL, verbose_name="Aprobado por",
    )
    calculated_scale = models.ForeignKey(
        on_delete=PROTECT, related_name="attendance_calculated_evaluations",
        to="grading.qualitativescale", verbose_name="Escala Calculada",
    )
    created_by = models.ForeignKey(
        null=True, on_delete=SET_NULL, related_name="behavior_evaluations_created",
        to=AUTH_USER_MODEL, verbose_name="Creado por",
    )
    enrollment = models.ForeignKey(
        on_delete=CASCADE, related_name="attendance_behavior_evaluations",
        to="students.enrollment", verbose_name="Matrícula",
    )
    evaluated_by = models.ForeignKey(
        null=True, on_delete=SET_NULL, related_name="behavior_evaluations",
        to=AUTH_USER_MODEL, verbose_name="Evaluado por",
    )
    final_scale = models.ForeignKey(
        blank=True, null=True, on_delete=PROTECT, related_name="attendance_final_evaluations",
        to="grading.qualitativescale", verbose_name="Escala Final",
    )

    class Meta:
        verbose_name = "Evaluación de Conducta"
        verbose_name_plural = "Evaluaciones de Conducta"
        unique_together = {("enrollment", "academic_period")}
        indexes = [
            Index(fields=["academic_period", "calculated_scale"]),
            Index(fields=["evaluated_by", "evaluation_date"]),
        ]
```

-- Corregido

```py
class BehaviorEvaluation(TimeStampedModel, SyncableModel):
    enrollment = models.ForeignKey(
        "students.Enrollment", on_delete=models.CASCADE,
        related_name="behavior_evaluations", verbose_name="Matrícula",
    )
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod", on_delete=models.CASCADE,
        related_name="behavior_evaluations", verbose_name="Período Académico",
    )
    evaluated_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True,
        related_name="behavior_evaluations", verbose_name="Evaluado por",
    )
    approved_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="behavior_evaluations_approved", verbose_name="Aprobado por",
    )
    created_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True,
        related_name="behavior_evaluations_created", verbose_name="Creado por",
    )
    calculated_scale = models.ForeignKey(
        "grading.QualitativeScale", on_delete=models.PROTECT,
        related_name="calculated_evaluations", verbose_name="Escala Calculada",
    )
    final_scale = models.ForeignKey(
        "grading.QualitativeScale", on_delete=models.PROTECT,
        null=True, blank=True, related_name="final_evaluations", verbose_name="Escala Final",
    )
    general_observation = models.TextField(blank=True, default="", verbose_name="Observación general")
    override_reason = models.TextField(blank=True, default="", verbose_name="Razón de anulación")
    evaluation_date = models.DateField(default=datetime.date.today, verbose_name="Fecha de evaluación")
    approval_date = models.DateField(null=True, blank=True, verbose_name="Fecha de aprobación")

    class Meta:
        app_label = "behavior"
        verbose_name = "Evaluación de Conducta"
        verbose_name_plural = "Evaluaciones de Conducta"
        unique_together = [("enrollment", "academic_period")]
        indexes = [
            models.Index(fields=["academic_period", "calculated_scale"]),
            models.Index(fields=["evaluated_by", "evaluation_date"]),
        ]
```

### Grading

- Resumen de Calificaciones del Período (PeriodGradeSummary)

-- Actual

```py
class PeriodGradeSummary(TimeStampedModel):
    formative_avg = models.DecimalField(decimal_places=2, max_digits=5, verbose_name="Promedio Formativo")
    summative_avg = models.DecimalField(decimal_places=2, max_digits=5, verbose_name="Promedio Sumativo")
    final_avg_truncated = models.DecimalField(decimal_places=2, max_digits=5, verbose_name="Promedio Final Truncado")
    is_failing = models.BooleanField(default=False, verbose_name="Está Reprobando")
    promotion_status = models.CharField(
        blank=True, choices=[("approved","Aprobado"),("failed","Reprobado")],
        max_length=20, null=True, verbose_name="Estado de Promoción",
    )
    calculated_at = models.DateTimeField(auto_now_add=True, verbose_name="Calculado en")
    academic_period = models.ForeignKey(
        on_delete=CASCADE, related_name="grade_summaries",
        to="academic.academicperiod", verbose_name="Período Académico",
    )
    approved_by = models.ForeignKey(
        blank=True, null=True, on_delete=SET_NULL, related_name="grade_summaries_approved",
        to=AUTH_USER_MODEL, verbose_name="Aprobado por",
    )
    calculated_by = models.ForeignKey(
        blank=True, null=True, on_delete=SET_NULL, related_name="grade_summaries_calculated",
        to=AUTH_USER_MODEL, verbose_name="Calculado por",
    )
    enrollment = models.ForeignKey(
        on_delete=CASCADE, related_name="grade_summaries",
        to="students.enrollment", verbose_name="Matrícula",
    )
    qualitative_scale = models.ForeignKey(
        blank=True, null=True, on_delete=PROTECT,
        to="grading.qualitativescale", verbose_name="Escala Cualitativa",
    )
    subject_offering = models.ForeignKey(
        on_delete=CASCADE, related_name="grade_summaries",
        to="academic.subjectoffering", verbose_name="Oferta de Asignatura",
    )

    class Meta:
        verbose_name = "Resumen de Calificaciones del Período"
        verbose_name_plural = "Resúmenes de Calificaciones del Período"
        constraints = [UniqueConstraint(fields=["enrollment","subject_offering","academic_period"], name="unique_period_grade_summary")]
        indexes = [
            Index(fields=["academic_period", "subject_offering"]),
            Index(fields=["enrollment", "academic_period"]),
            Index(fields=["is_failing", "academic_period"]),
        ]
```

-- Corregido

```py
class PeriodGradeSummary(TimeStampedModel):
    enrollment = models.ForeignKey(
        "students.Enrollment", on_delete=models.CASCADE,
        related_name="grade_summaries", verbose_name="Matrícula",
    )
    subject_offering = models.ForeignKey(
        "academic.SubjectOffering", on_delete=models.CASCADE,
        related_name="grade_summaries", verbose_name="Oferta de Asignatura",
    )
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod", on_delete=models.CASCADE,
        related_name="grade_summaries", verbose_name="Período Académico",
    )
    formative_avg = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Promedio Formativo")
    summative_avg = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Promedio Sumativo")
    final_avg_truncated = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Promedio Final Truncado")
    qualitative_scale = models.ForeignKey(
        "grading.QualitativeScale", on_delete=models.PROTECT,
        null=True, blank=True, verbose_name="Escala Cualitativa",
    )
    is_failing = models.BooleanField(default=False, verbose_name="Está Reprobando")
    promotion_status = models.CharField(
        max_length=20, choices=PromotionStatusChoices.choices,
        null=True, blank=True, verbose_name="Estado de Promoción",
    )
    calculated_at = models.DateTimeField(auto_now_add=True, verbose_name="Calculado en")
    calculated_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="grade_summaries_calculated", verbose_name="Calculado por",
    )
    approved_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="grade_summaries_approved", verbose_name="Aprobado por",
    )

    class Meta:
        app_label = "grading"
        verbose_name = "Resumen de Calificaciones del Período"
        verbose_name_plural = "Resúmenes de Calificaciones del Período"
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "subject_offering", "academic_period"],
                name="unique_period_grade_summary",
            ),
        ]
        indexes = [
            models.Index(fields=["academic_period", "subject_offering"]),
            models.Index(fields=["enrollment", "academic_period"]),
            models.Index(fields=["is_failing", "academic_period"]),
        ]
```

- Historial de Cambio de Calificación (GradeChangeHistory)

-- Actual

```py
class GradeChangeHistory(TimeStampedModel):
    previous_score = models.DecimalField(decimal_places=2, max_digits=5, verbose_name="Nota Anterior")
    new_score = models.DecimalField(decimal_places=2, max_digits=5, verbose_name="Nota Nueva")
    reason = models.TextField(verbose_name="Razón del Cambio")
    reason_code = models.CharField(blank=True, max_length=30, verbose_name="Código de Razón")
    origin = models.CharField(
        choices=[("MANUAL","Manual"),("IMPORT","Importación"),("SYNC","Sincronización")],
        default="MANUAL", max_length=20, verbose_name="Origen",
    )
    device_origin = models.CharField(blank=True, max_length=40, null=True, verbose_name="Dispositivo de Origen")
    modified_at = models.DateTimeField(auto_now_add=True, verbose_name="Modificado en")
    created_by = models.ForeignKey(
        blank=True, null=True, on_delete=SET_NULL, related_name="grade_changes_created",
        to=AUTH_USER_MODEL, verbose_name="Creado por",
    )
    modified_by_user = models.ForeignKey(
        null=True, on_delete=SET_NULL, to=AUTH_USER_MODEL, verbose_name="Modificado por",
    )
    new_qualitative = models.ForeignKey(
        blank=True, null=True, on_delete=SET_NULL, related_name="new_grade_changes",
        to="grading.qualitativescale", verbose_name="Nueva Escala Cualitativa",
    )
    previous_qualitative = models.ForeignKey(
        blank=True, null=True, on_delete=SET_NULL, related_name="previous_grade_changes",
        to="grading.qualitativescale", verbose_name="Escala Cualitativa Anterior",
    )
    student_note = models.ForeignKey(
        on_delete=CASCADE, related_name="change_history",
        to="grading.studentnote", verbose_name="Nota",
    )

    class Meta:
        verbose_name = "Historial de Cambio de Calificación"
        verbose_name_plural = "Historiales de Cambio de Calificación"
        ordering = ["-modified_at"]
        indexes = [
            Index(fields=["student_note", "modified_at"]),
            Index(fields=["modified_by_user", "modified_at"]),
        ]
```

-- Corregido

```py
class GradeChangeHistory(TimeStampedModel):
    student_note = models.ForeignKey(
        "grading.StudentNote", on_delete=models.CASCADE,
        related_name="change_history", verbose_name="Nota",
    )
    modified_by_user = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, verbose_name="Modificado por",
    )
    created_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="grade_changes_created", verbose_name="Creado por",
    )
    previous_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Nota Anterior")
    new_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Nota Nueva")
    previous_qualitative = models.ForeignKey(
        "grading.QualitativeScale", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="previous_grade_changes",
        verbose_name="Escala Cualitativa Anterior",
    )
    new_qualitative = models.ForeignKey(
        "grading.QualitativeScale", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="new_grade_changes",
        verbose_name="Nueva Escala Cualitativa",
    )
    reason = models.TextField(verbose_name="Razón del Cambio")
    reason_code = models.CharField(max_length=30, blank=True, verbose_name="Código de Razón")
    origin = models.CharField(
        max_length=20,
        choices=[("MANUAL","Manual"),("IMPORT","Importación"),("SYNC","Sincronización")],
        default="MANUAL", verbose_name="Origen",
    )
    device_origin = models.CharField(max_length=40, null=True, blank=True, verbose_name="Dispositivo de Origen")
    modified_at = models.DateTimeField(auto_now_add=True, verbose_name="Modificado en")

    class Meta:
        app_label = "grading"
        verbose_name = "Historial de Cambio de Calificación"
        verbose_name_plural = "Historiales de Cambio de Calificación"
        ordering = ["-modified_at"]
        indexes = [
            models.Index(fields=["student_note", "modified_at"]),
            models.Index(fields=["modified_by_user", "modified_at"]),
        ]
```

### Resumen de cambios clave

| Aspecto                                                                                        | Migración (Actual)                                                                                     | Modelo Python (Corregido)                                             |
| ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------- |
| `Person.birth_date`                                                                            | nullable                                                                                               | NOT NULL                                                              |
| `Person.city`                                                                                  | NO existe                                                                                              | FK a `people.City`                                                    |
| `City` (modelo)                                                                                | NO existe                                                                                              | Creado                                                                |
| `SchoolYear.name`                                                                              | existe                                                                                                 | NO existe                                                             |
| `AcademicGrade.sequence_order`                                                                 | existe                                                                                                 | NO existe                                                             |
| `AcademicGrade.ordering`                                                                       | `["sequence_order"]`                                                                                   | `["name"]`                                                            |
| `SubjectAcademicConfig.pedagogical_order`                                                      | existe                                                                                                 | NO existe                                                             |
| `SubjectAcademicConfig.ordering`                                                               | `["pedagogical_order"]`                                                                                | `["subject"]`                                                         |
| `AcademicPeriod.parent_period`                                                                 | existe                                                                                                 | NO existe                                                             |
| `User.email`                                                                                   | existe                                                                                                 | NO existe explícitamente                                              |
| `Student.person`                                                                               | existe                                                                                                 | NO existe                                                             |
| `Student.residential_zone`                                                                     | existe                                                                                                 | NO existe                                                             |
| `Student.distance_to_school_km`                                                                | existe                                                                                                 | NO existe                                                             |
| `StudentRepresentative.person`                                                                 | existe                                                                                                 | NO existe                                                             |
| `StudentRepresentative.can_pickup`                                                             | existe                                                                                                 | NO existe                                                             |
| `StudentRepresentative.user` (FK a iam.User)                                                   | NO existe                                                                                              | existe                                                                |
| `Enrollment.approved_by`                                                                       | existe                                                                                                 | NO existe                                                             |
| `Enrollment.created_by`                                                                        | existe                                                                                                 | NO existe                                                             |
| `Enrollment.repeated_school_year`                                                              | existe                                                                                                 | NO existe                                                             |
| `ResidentialZone` (modelo)                                                                     | existe en migración                                                                                    | NO existe (eliminar)                                                  |
| `EnrollmentHistory` (modelo)                                                                   | existe en migración                                                                                    | NO existe (eliminar)                                                  |
| `Attendance.created_by` / `modified_by`                                                        | existen                                                                                                | NO existen                                                            |
| `Severity.numeric_level`                                                                       | existe                                                                                                 | NO existe                                                             |
| `Severity.ordering`                                                                            | `["numeric_level"]`                                                                                    | `["name"]`                                                            |
| `ConductIncident.approved_by/created_by/modified_by/reported_by_user`                          | existen                                                                                                | NO existen                                                            |
| `BehaviorEvaluation` `related_name` en enrollment/academic_period/calculated_scale/final_scale | `attendance_behavior_evaluations`, `attendance_calculated_evaluations`, `attendance_final_evaluations` | `behavior_evaluations`, `calculated_evaluations`, `final_evaluations` |
| `PeriodGradeSummary.calculated_by`                                                             | existe                                                                                                 | existe (mismo)                                                        |
| `PeriodGradeSummary.approved_by`                                                               | existe                                                                                                 | existe (mismo)                                                        |
| `GradeChangeHistory.modified_by_user`                                                          | existe                                                                                                 | existe (mismo)                                                        |
| `GradeChangeHistory.created_by`                                                                | existe                                                                                                 | existe (mismo)                                                        |
