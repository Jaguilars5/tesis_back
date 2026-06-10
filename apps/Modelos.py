
from django.db import models
from apps.core.models import TimeStampedModel


def _get_default_period_type():
    from apps.academic.models import PeriodType
    obj, _ = PeriodType.objects.get_or_create(code="REGULAR", defaults={"name": "Regular"})
    return obj.pk


class AcademicPeriod(TimeStampedModel):
    code = models.CharField(max_length=50, blank=True, db_index=True, verbose_name="Código")
    school_year = models.ForeignKey(
        "institutions.SchoolYear",
        on_delete=models.CASCADE,
        verbose_name="Año Escolar",
    )
    parent_period = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="child_periods",
        verbose_name="Período Padre",
    )
    name = models.CharField(max_length=80, verbose_name="Nombre del Período")
    period_type = models.ForeignKey("academic.PeriodType", on_delete=models.PROTECT, default=_get_default_period_type, verbose_name="Tipo de período")
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    end_date = models.DateField(verbose_name="Fecha de Fin")
    is_regular_period = models.BooleanField(
        default=True, verbose_name="Período Regular"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "academic"
        verbose_name = "Período Académico"
        verbose_name_plural = "Períodos Académicos"

    def __str__(self):
        return self.name
from django.db import models
from apps.core.models import TimeStampedModel


class ClassSchedule(TimeStampedModel):
    subject_offering = models.ForeignKey(
        "academic.SubjectOffering",
        on_delete=models.CASCADE,
        related_name="schedules",
        verbose_name="Oferta de Materia",
    )
    day_of_week = models.ForeignKey(
        "academic.DayOfWeek",
        on_delete=models.PROTECT,
        verbose_name="Día de la Semana",
    )
    start_time = models.TimeField(verbose_name="Hora de inicio")
    end_time = models.TimeField(verbose_name="Hora de fin")
    classroom = models.CharField(max_length=50, blank=True, verbose_name="Aula")
    building = models.CharField(max_length=50, blank=True, verbose_name="Edificio")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "academic"
        verbose_name = "Horario Académico"
        verbose_name_plural = "Horarios Académicos"
        unique_together = [("subject_offering", "day_of_week", "start_time")]
        ordering = ["day_of_week", "start_time"]

    def __str__(self):
        return f"{self.subject_offering} - {self.day_of_week} ({self.start_time}-{self.end_time})"
from django.db import models
from apps.core.models import TimeStampedModel


class DayOfWeek(TimeStampedModel):
    code = models.IntegerField(unique=True, verbose_name="Código (1-7)")
    name = models.CharField(max_length=20, verbose_name="Nombre del día")

    class Meta:
        app_label = "academic"
        verbose_name = "Día de la Semana"
        verbose_name_plural = "Días de la Semana"
        ordering = ["code"]

    def __str__(self):
        return self.name
from django.db import models
from apps.core.models import TimeStampedModel


class InterdisciplinaryProject(TimeStampedModel):
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod",
        on_delete=models.CASCADE,
        related_name="interdisciplinary_projects",
        verbose_name="Período Académico",
    )
    subject_offerings = models.ManyToManyField(
        "academic.SubjectOffering",
        through="academic.SubjectProject",
        verbose_name="Ofertas de Materia",
    )
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    start_date = models.DateField(verbose_name="Fecha de inicio")
    delivery_date = models.DateField(verbose_name="Fecha de entrega")
    product_max_score = models.DecimalField(
        max_digits=5, decimal_places=2, default=10.00,
        verbose_name="Puntaje máximo del producto",
    )
    presentation_max_score = models.DecimalField(
        max_digits=5, decimal_places=2, default=10.00,
        verbose_name="Puntaje máximo de la presentación",
    )
    product_rubric = models.TextField(null=True, blank=True, verbose_name="Rúbrica del producto")
    presentation_rubric = models.TextField(null=True, blank=True, verbose_name="Rúbrica de la presentación")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "academic"
        verbose_name = "Proyecto Interdisciplinario"
        verbose_name_plural = "Proyectos Interdisciplinarios"
        ordering = ["-start_date"]

    def __str__(self):
        return self.title
from django.db import models
from apps.core.models import TimeStampedModel


class PeriodType(TimeStampedModel):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "academic"
        verbose_name = "Tipo de Período"
        verbose_name_plural = "Tipos de Período"
        ordering = ["name"]

    def __str__(self):
        return self.name
from django.db import models
from apps.core.models import TimeStampedModel


class SubjectAcademicConfig(TimeStampedModel):
    subject = models.ForeignKey(
        "academic.Subject",
        on_delete=models.CASCADE,
        verbose_name="Materia",
    )
    academic_grade = models.ForeignKey(
        "institutions.AcademicGrade",
        on_delete=models.CASCADE,
        verbose_name="Grado Académico",
    )
    weekly_hours = models.IntegerField(verbose_name="Horas Semanales")
    pedagogical_order = models.IntegerField(verbose_name="Orden Pedagógico")
    is_required = models.BooleanField(default=True, verbose_name="Obligatoria")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "academic"
        verbose_name = "Configuración de Materia por Grado"
        verbose_name_plural = "Configuraciones de Materia por Grado"
        ordering = ["pedagogical_order"]
        unique_together = [("subject", "academic_grade")]

    def __str__(self):
        return f"{self.subject.name} - {self.academic_grade.name}"
from django.db import models
from apps.core.models import TimeStampedModel


class SubjectOffering(TimeStampedModel):
    school_year = models.ForeignKey(
        "institutions.SchoolYear",
        on_delete=models.CASCADE,
        verbose_name="Año Escolar",
    )
    section = models.ForeignKey(
        "institutions.Section",
        on_delete=models.CASCADE,
        verbose_name="Sección",
    )
    subject_academic_config = models.ForeignKey(
        "academic.SubjectAcademicConfig",
        on_delete=models.CASCADE,
        verbose_name="Configuración de Materia",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "academic"
        verbose_name = "Oferta de Materia"
        verbose_name_plural = "Ofertas de Materias"
        unique_together = ("school_year", "section", "subject_academic_config")
        indexes = [
            models.Index(fields=["section", "school_year"]),
        ]

    def __str__(self):
        return f"{self.school_year} - {self.section} - {self.subject_academic_config}"
from django.db import models
from apps.core.models import TimeStampedModel


class SubjectProject(TimeStampedModel):
    interdisciplinary_project = models.ForeignKey(
        "academic.InterdisciplinaryProject",
        on_delete=models.CASCADE,
        related_name="subject_projects",
        verbose_name="Proyecto Interdisciplinario",
    )
    subject_offering = models.ForeignKey(
        "academic.SubjectOffering",
        on_delete=models.CASCADE,
        related_name="subject_projects",
        verbose_name="Oferta de Asignatura",
    )
    responsible_teacher = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True,
        verbose_name="Docente responsable",
    )

    class Meta:
        app_label = "academic"
        verbose_name = "Asignatura del Proyecto"
        verbose_name_plural = "Asignaturas del Proyecto"
        unique_together = ("interdisciplinary_project", "subject_offering")

    def __str__(self):
        return f"{self.interdisciplinary_project.title} - {self.subject_offering}"
from django.db import models
from apps.core.models import TimeStampedModel


class Subject(TimeStampedModel):
    name = models.CharField(max_length=255, verbose_name="Nombre de la Materia")
    code = models.CharField(max_length=100, unique=True, verbose_name="Código")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    class Meta:
        app_label = "academic"
        verbose_name = "Materia"
        verbose_name_plural = "Materias"

    def __str__(self):
        return self.name
from django.db import models
from apps.core.models import TimeStampedModel


class TeacherSubjectSection(TimeStampedModel):
    user = models.ForeignKey(
        "iam.User", on_delete=models.CASCADE, verbose_name="Docente"
    )
    subject_offering = models.ForeignKey(
        "academic.SubjectOffering",
        on_delete=models.CASCADE,
        verbose_name="Oferta de Materia",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    class Meta:
        app_label = "academic"
        verbose_name = "Docente-Materia-Sección"
        verbose_name_plural = "Docentes-Materias-Secciones"
        unique_together = [("user", "subject_offering")]
        indexes = [
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.subject_offering}"
-Analytics:
from django.db import models
from apps.core.models import TimeStampedModel


class AlertType(TimeStampedModel):
    code = models.CharField(max_length=50, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "analytics"
        verbose_name = "Tipo de Alerta"
        verbose_name_plural = "Tipos de Alerta"
        ordering = ["name"]

    def __str__(self):
        return self.name
from django.db import models
from apps.core.models import TimeStampedModel


class DashboardMetric(TimeStampedModel):
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod", on_delete=models.CASCADE,
        verbose_name="Período Académico",
    )
    section = models.ForeignKey(
        "institutions.Section", on_delete=models.CASCADE, null=True, blank=True,
        verbose_name="Sección",
    )
    academic_grade = models.ForeignKey(
        "institutions.AcademicGrade", on_delete=models.CASCADE, null=True, blank=True,
        verbose_name="Grado Académico",
    )
    metric_type = models.CharField(max_length=50, verbose_name="Tipo de Métrica")
    metric_value = models.JSONField(default=dict, verbose_name="Valor de la Métrica")
    metric_schema_version = models.CharField(max_length=10, blank=True, default="1.0", verbose_name="Versión del Esquema")
    calculated_at = models.DateTimeField(auto_now_add=True, verbose_name="Calculado en")

    class Meta:
        app_label = "analytics"
        verbose_name = "Métrica de Dashboard"
        verbose_name_plural = "Métricas de Dashboard"
        unique_together = [("academic_period", "section", "metric_type")]
        indexes = [
            models.Index(fields=["academic_period", "metric_type"]),
            models.Index(fields=["calculated_at"]),
        ]

    def __str__(self):
        return f"{self.metric_type} - {self.academic_period}"
from django.db import models
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class EarlyAlert(TimeStampedModel, SyncableModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="early_alerts",
        verbose_name="Matrícula",
    )
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod",
        on_delete=models.CASCADE,
        related_name="early_alerts",
        verbose_name="Período Académico",
    )
    alert_type = models.ForeignKey("analytics.AlertType", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tipo de alerta")
    description = models.TextField(verbose_name="Descripción")
    urgency_level = models.ForeignKey("analytics.UrgencyLevel", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Nivel de urgencia")
    attended = models.BooleanField(default=False, verbose_name="Atendida")
    attended_by_user = models.ForeignKey(
        "iam.User",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="attended_alerts",
        verbose_name="Atendida por",
    )
    detected_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de detección")
    attended_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de atención")
    response_actions = models.TextField(null=True, blank=True, verbose_name="Acciones de respuesta")

    class Meta:
        app_label = "analytics"
        verbose_name = "Alerta Temprana"
        verbose_name_plural = "Alertas Tempranas"
        ordering = ["-detected_at"]
        indexes = [
            models.Index(fields=["attended", "urgency_level"]),
            models.Index(fields=["enrollment", "academic_period"]),
        ]

    def __str__(self):
        return f"{self.alert_type.name if self.alert_type else ''} - {self.enrollment} ({self.urgency_level.name if self.urgency_level else ''})"
from django.db import models
from apps.core.models import TimeStampedModel


class RiskFactor(TimeStampedModel):
    code = models.CharField(max_length=30, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        app_label = "analytics"
        verbose_name = "Factor de Riesgo"
        verbose_name_plural = "Factores de Riesgo"
        ordering = ["name"]

    def __str__(self):
        return self.name
from django.db import models
from apps.core.models import TimeStampedModel


class StudentFeatureSnapshot(TimeStampedModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        verbose_name="Matrícula",
        help_text="Matrícula del estudiante",
        null=True,  # Permite null temporal para facilitar migraciones desde el modelo antiguo
    )
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod",
        on_delete=models.CASCADE,
        verbose_name="Período Académico",
    )
    attendance_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, verbose_name="Tasa de Asistencia"
    )
    consecutive_absences_max = models.IntegerField(
        default=0, verbose_name="Máximo de Faltas Consecutivas"
    )
    tardiness_count = models.IntegerField(default=0, verbose_name="Contador de Atrasos")
    justified_absences = models.IntegerField(
        default=0, verbose_name="Ausencias Justificadas"
    )
    unjustified_absences = models.IntegerField(
        default=0, verbose_name="Ausencias Injustificadas"
    )
    formative_avg_normalized = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, verbose_name="Promedio Formativo Normalizado"
    )
    summative_avg_normalized = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, verbose_name="Promedio Sumativo Normalizado"
    )
    grade_trend_slope = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, verbose_name="Tendencia de Notas"
    )
    failing_subjects_count = models.IntegerField(
        default=0, verbose_name="Materias Reprobadas"
    )
    conduct_score = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, verbose_name="Puntaje de Conducta"
    )
    severe_incidents_count = models.IntegerField(
        default=0, verbose_name="Incidentes Graves"
    )
    family_notified_ratio = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, verbose_name="Ratio de Notificación Familiar"
    )
    prev_period_avg_grade = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Promedio Período Anterior",
    )
    age_grade_gap = models.IntegerField(default=0, verbose_name="Brecha Edad-Grado")
    is_repeat = models.BooleanField(default=False, verbose_name="Es Repitente")
    has_special_needs = models.BooleanField(
        default=False, verbose_name="Tiene NEE"
    )
    active_alerts = models.IntegerField(default=0, verbose_name="Alertas Activas")
    is_current = models.BooleanField(default=False, verbose_name="Es actual")
    snapshot_trigger = models.CharField(
        max_length=10,
        choices=[("MANUAL", "Manual"), ("AUTO", "Automático"), ("BATCH", "Por Lote")],
        default="MANUAL",
        verbose_name="Desencadenante",
    )
    calculated_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Cálculo")

    class Meta:
        app_label = "analytics"
        verbose_name = "Instantánea de Métricas de Estudiante"
        verbose_name_plural = "Instantáneas de Métricas de Estudiantes"
        unique_together = [("enrollment", "academic_period")]
        indexes = [
            models.Index(fields=["academic_period", "failing_subjects_count"]),
            models.Index(fields=["academic_period", "attendance_rate"]),
            models.Index(fields=["calculated_at"]),
        ]

    def __str__(self):
        return f"Features for {self.enrollment} ({self.academic_period})"
from django.db import models
from apps.core.models import TimeStampedModel


class StudentRiskFactor(TimeStampedModel):
    student_risk_score = models.ForeignKey(
        "analytics.StudentRiskScore",
        on_delete=models.CASCADE,
        related_name="risk_factors",
        verbose_name="Puntaje de Riesgo",
    )
    risk_factor = models.ForeignKey(
        "analytics.RiskFactor",
        on_delete=models.CASCADE,
        verbose_name="Factor de Riesgo",
    )
    contribution_weight = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Peso de Contribución (%)"
    )

    class Meta:
        app_label = "analytics"
        verbose_name = "Factor de Riesgo del Estudiante"
        verbose_name_plural = "Factores de Riesgo de los Estudiantes"
        unique_together = ("student_risk_score", "risk_factor")

    def __str__(self):
        return f"{self.student_risk_score} - {self.risk_factor.name} ({self.contribution_weight}%)"
from django.db import models
from apps.core.models import TimeStampedModel


class StudentRiskScore(TimeStampedModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        verbose_name="Matrícula",
        null=True,  # Permite null temporal para facilitar migraciones desde el modelo antiguo
    )
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod",
        on_delete=models.CASCADE,
        verbose_name="Período Académico",
    )
    risk_score = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, verbose_name="Puntaje de Riesgo",
    )
    risk_label = models.CharField(
        max_length=20, default="", verbose_name="Etiqueta de Riesgo",
    )
    model_version = models.CharField(
        max_length=50, default="", verbose_name="Versión del Modelo",
    )
    calculated_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Cálculo",
    )

    class Meta:
        app_label = "analytics"
        ordering = ["-calculated_at"]
        verbose_name = "Puntaje de Riesgo del Estudiante"
        verbose_name_plural = "Puntajes de Riesgo de los Estudiantes"
        unique_together = [("enrollment", "academic_period")]
        indexes = [
            models.Index(fields=["academic_period", "risk_label"]),
            models.Index(fields=["calculated_at"]),
        ]

    def __str__(self):
        return f"{self.enrollment} - {self.risk_label} ({self.risk_score})"
from django.db import models
from apps.core.models import TimeStampedModel


class UrgencyLevel(TimeStampedModel):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "analytics"
        verbose_name = "Nivel de Urgencia"
        verbose_name_plural = "Niveles de Urgencia"
        ordering = ["name"]

    def __str__(self):
        return self.name

-Attendance:
from django.db import models
from apps.core.models import TimeStampedModel


class AbsenceType(TimeStampedModel):
    code = models.CharField(max_length=30, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "attendance"
        verbose_name = "Tipo de Ausencia"
        verbose_name_plural = "Tipos de Ausencia"
        ordering = ["name"]

    def __str__(self):
        return self.name
from django.db import models
from apps.core.models import TimeStampedModel


class AttendanceStatus(TimeStampedModel):
    code = models.CharField(max_length=10, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    tipo = models.CharField(
        max_length=10,
        choices=[("POSITIVO", "Positivo"), ("NEGATIVO", "Negativo")],
        null=True, blank=True, verbose_name="Tipo",
    )

    class Meta:
        app_label = "attendance"
        verbose_name = "Estado de Asistencia"
        verbose_name_plural = "Estados de Asistencia"
        ordering = ["name"]

    def __str__(self):
        return self.name
from django.db import models
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class Attendance(TimeStampedModel, SyncableModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="attendance_records",
        verbose_name="Matrícula",
    )
    teacher_subject_section = models.ForeignKey(
        "academic.TeacherSubjectSection",
        on_delete=models.CASCADE,
        related_name="attendance_records",
        verbose_name="Clase",
    )
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod",
        on_delete=models.CASCADE,
        related_name="attendance_records",
        verbose_name="Período Académico",
    )
    attendance_status = models.ForeignKey(
        "attendance.AttendanceStatus",
        on_delete=models.PROTECT,
        verbose_name="Estado",
        null=True,
    )
    attendance_date = models.DateField(verbose_name="Fecha", null=True)
    absence_type = models.ForeignKey("attendance.AbsenceType", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tipo de ausencia")
    observation = models.TextField(null=True, blank=True, verbose_name="Observaciones")
    created_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="attendances_created", verbose_name="Creado por",
    )
    modified_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="attendances_modified", verbose_name="Modificado por",
    )

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

    def __str__(self):
        return f"{self.enrollment} - {self.attendance_date} - {self.attendance_status}"

-Behavior:
from datetime import date
from django.db import models
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class BehaviorEvaluation(TimeStampedModel, SyncableModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="attendance_behavior_evaluations",
        verbose_name="Matrícula",
    )
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod",
        on_delete=models.CASCADE,
        related_name="attendance_behavior_evaluations",
        verbose_name="Período Académico",
    )
    calculated_scale = models.ForeignKey(
        "grading.QualitativeScale",
        on_delete=models.PROTECT,
        related_name="attendance_calculated_evaluations",
        verbose_name="Escala Calculada",
    )
    final_scale = models.ForeignKey(
        "grading.QualitativeScale",
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="attendance_final_evaluations",
        verbose_name="Escala Final",
    )
    general_observation = models.TextField(null=True, blank=True, verbose_name="Observación general")
    override_reason = models.TextField(null=True, blank=True, verbose_name="Razón de anulación")
    created_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True,
        related_name="behavior_evaluations_created", verbose_name="Creado por",
    )
    evaluated_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True,
        related_name="behavior_evaluations", verbose_name="Evaluado por",
    )
    approved_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="behavior_evaluations_approved", verbose_name="Aprobado por",
    )
    evaluation_date = models.DateField(default=date.today, verbose_name="Fecha de evaluación")
    approval_date = models.DateField(null=True, blank=True, verbose_name="Fecha de aprobación")

    class Meta:
        app_label = "behavior"
        verbose_name = "Evaluación de Conducta"
        verbose_name_plural = "Evaluaciones de Conducta"
        unique_together = ("enrollment", "academic_period")
        indexes = [
            models.Index(fields=["academic_period", "calculated_scale"]),
            models.Index(fields=["evaluated_by", "evaluation_date"]),
        ]

    def __str__(self):
        return f"{self.enrollment} - {self.academic_period} ({self.calculated_scale})"
from django.db import models
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class ConductIncident(TimeStampedModel, SyncableModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="conduct_incidents",
        verbose_name="Matrícula",
        null=True,
    )
    reported_by_user = models.ForeignKey(
        "iam.User",
        on_delete=models.SET_NULL,
        related_name="reported_conduct_incidents",
        null=True,
        verbose_name="Reportado por",
    )
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod",
        on_delete=models.CASCADE,
        related_name="conduct_incidents",
        verbose_name="Período Académico",
    )
    incident_type = models.ForeignKey(
        "behavior.IncidentType",
        on_delete=models.PROTECT,
        verbose_name="Tipo de incidente",
        null=True,
    )
    incident_date = models.DateField(verbose_name="Fecha del Incidente")
    severity = models.ForeignKey(
        "behavior.Severity",
        on_delete=models.PROTECT,
        verbose_name="Severidad",
    )
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    actions_taken = models.TextField(null=True, blank=True, verbose_name="Acciones tomadas")
    family_notified = models.BooleanField(default=False, verbose_name="Familia Notificada")
    created_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="incidents_created", verbose_name="Creado por",
    )
    modified_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="incidents_modified", verbose_name="Modificado por",
    )
    approved_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="incidents_approved", verbose_name="Aprobado por",
    )

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

    def __init__(self, *args, **kwargs):
        category = kwargs.pop("category", None)
        super().__init__(*args, **kwargs)
        if category:
            from apps.behavior.models import IncidentType
            incident_type, _ = IncidentType.objects.get_or_create(
                code=category,
                defaults={"name": category.capitalize(), "description": f"Tipo de incidente: {category}"}
            )
            self.incident_type = incident_type

    @property
    def category(self):
        return self.incident_type.code if self.incident_type else ""

    @category.setter
    def category(self, value):
        if value:
            from apps.behavior.models import IncidentType
            incident_type, _ = IncidentType.objects.get_or_create(
                code=value,
                defaults={"name": value.capitalize(), "description": f"Tipo de incidente: {value}"}
            )
            self.incident_type = incident_type
        else:
            self.incident_type = None

    def __str__(self):
        category_str = self.category if self.category else (str(self.incident_type) if self.incident_type else "")
        return f"{self.enrollment} - {category_str} ({self.incident_date})"
from django.db import models


class DevelopmentLevel(models.Model):
    code = models.CharField(max_length=30, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "behavior"
        verbose_name = "Nivel de Desarrollo"
        verbose_name_plural = "Niveles de Desarrollo"
        ordering = ["name"]

    def __str__(self):
        return self.name

from django.db import models
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class DiagnosticEvaluation(TimeStampedModel, SyncableModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="diagnostic_evaluations",
        verbose_name="Matrícula",
    )
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod",
        on_delete=models.CASCADE,
        related_name="diagnostic_evaluations",
        verbose_name="Período Académico",
    )
    applied_by_user = models.ForeignKey(
        "iam.User",
        on_delete=models.CASCADE,
        related_name="diagnostic_evaluations",
        verbose_name="Aplicada por",
    )
    socioemotional_area = models.ForeignKey(
        "behavior.SocioemotionalArea",
        on_delete=models.PROTECT,
        verbose_name="Área Socioemocional",
    )
    findings_description = models.TextField(verbose_name="Descripción de hallazgos")
    development_level = models.ForeignKey(
        "behavior.DevelopmentLevel",
        on_delete=models.PROTECT,
        verbose_name="Nivel de Desarrollo",
    )
    application_date = models.DateField(verbose_name="Fecha de aplicación")
    recommendations = models.TextField(null=True, blank=True, verbose_name="Recomendaciones")

    class Meta:
        app_label = "behavior"
        verbose_name = "Evaluación Diagnóstica"
        verbose_name_plural = "Evaluaciones Diagnósticas"
        ordering = ["-application_date"]

    def __str__(self):
        return f"{self.enrollment} - {self.socioemotional_area} ({self.application_date})"

from django.db import models
from apps.core.models import TimeStampedModel


class IncidentType(TimeStampedModel):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "behavior"
        verbose_name = "Tipo de Incidente"
        verbose_name_plural = "Tipos de Incidente"
        ordering = ["name"]

    def __str__(self):
        return self.name

from django.db import models


class Severity(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    numeric_level = models.IntegerField(verbose_name="Nivel Numérico")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "behavior"
        verbose_name = "Severidad"
        verbose_name_plural = "Severidades"
        ordering = ["numeric_level"]

    def __str__(self):
        return self.name
    
from django.db import models
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class SkillEvaluation(TimeStampedModel, SyncableModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="skill_evaluations",
        verbose_name="Matrícula",
    )
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod",
        on_delete=models.CASCADE,
        related_name="skill_evaluations",
        verbose_name="Período Académico",
    )
    socioemotional_skill = models.ForeignKey(
        "behavior.SocioemotionalSkill",
        on_delete=models.CASCADE,
        related_name="evaluations",
        verbose_name="Habilidad",
    )
    qualitative_scale = models.ForeignKey(
        "grading.QualitativeScale",
        on_delete=models.PROTECT,
        verbose_name="Escala Cualitativa",
    )
    observation = models.TextField(null=True, blank=True, verbose_name="Observación")
    evaluation_date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Evaluación")

    class Meta:
        app_label = "behavior"
        verbose_name = "Evaluación de Habilidad"
        verbose_name_plural = "Evaluaciones de Habilidades"
        unique_together = ("enrollment", "academic_period", "socioemotional_skill")
        indexes = [
            models.Index(fields=["academic_period", "socioemotional_skill"]),
        ]

    def __str__(self):
        return f"{self.enrollment} - {self.socioemotional_skill.name}"


from django.db import models


class SocioemotionalArea(models.Model):
    code = models.CharField(max_length=30, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "behavior"
        verbose_name = "Área Socioemocional"
        verbose_name_plural = "Áreas Socioemocionales"
        ordering = ["name"]

    def __str__(self):
        return self.name
    
from django.db import models
from apps.core.models import TimeStampedModel


class SocioemotionalSkill(TimeStampedModel):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activa")

    class Meta:
        app_label = "behavior"
        verbose_name = "Habilidad Socioemocional"
        verbose_name_plural = "Habilidades Socioemocionales"
        ordering = ["name"]

    def __str__(self):
        return self.name


-Configuracion;

from django.db import models
from apps.core.models import TimeStampedModel


class SystemConfig(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)
    key = models.CharField(max_length=255, unique=True, verbose_name="Clave")
    value = models.TextField(verbose_name="Valor")
    description = models.TextField(blank=True, verbose_name="Descripción")

    class Meta:
        app_label = "configuration"
        verbose_name = "Configuración del Sistema"
        verbose_name_plural = "Configuraciones del Sistema"

    def __str__(self):
        return self.key

-Core:
from django.db import models
from apps.core.models import TimeStampedModel


class AuditLog(TimeStampedModel):
    user = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True,
        verbose_name="Usuario",
    )
    action = models.CharField(max_length=20, choices=[
        ("CREATE", "Creación"),
        ("UPDATE", "Modificación"),
        ("DELETE", "Eliminación"),
        ("RECOVER", "Recuperación"),
    ], verbose_name="Acción")
    model_name = models.CharField(max_length=100, verbose_name="Modelo")
    record_id = models.CharField(max_length=36, verbose_name="ID del Registro")
    changes = models.JSONField(default=dict, blank=True, verbose_name="Cambios")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Dirección IP")
    user_agent = models.CharField(max_length=255, blank=True, verbose_name="User-Agent")

    class Meta:
        app_label = "core"
        verbose_name = "Bitácora de Auditoría"
        verbose_name_plural = "Bitácoras de Auditoría"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["model_name", "record_id"]),
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["action", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.action} - {self.model_name}#{self.record_id} ({self.user})"

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Actualización")

    class Meta:
        abstract = True
-Grading:
from django.db import models
from apps.core.models import TimeStampedModel


class ActivityType(TimeStampedModel):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "grading"
        verbose_name = "Tipo de Actividad"
        verbose_name_plural = "Tipos de Actividad"
        ordering = ["name"]

    def __str__(self):
        return self.name

from django.db import models
from apps.core.models import TimeStampedModel


class BlockComponent(TimeStampedModel):
    """
    COMPONENTE_BLOQUE — Componentes dentro de un bloque de evaluación.
    Configuración pedagógica del docente; baja frecuencia de cambio.
    """

    code = models.CharField(max_length=50, blank=True, db_index=True, verbose_name="Código")
    evaluation_block = models.ForeignKey(
        "grading.EvaluationBlock",
        on_delete=models.CASCADE,
        related_name="components",
        verbose_name="Bloque de Evaluación",
    )
    name = models.CharField(max_length=100, verbose_name="Nombre")
    internal_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Ponderación Interna (%)",
        help_text="Peso del componente dentro del bloque de evaluación",
    )

    class Meta:
        app_label = "grading"
        verbose_name = "Componente de Bloque"
        verbose_name_plural = "Componentes de Bloque"
        ordering = ["evaluation_block", "name"]

    def __str__(self):
        return f"{self.evaluation_block.name} — {self.name}"
from django.db import models
from apps.core.models import TimeStampedModel


class ComponentIndicator(TimeStampedModel):
    """
    INDICADOR_COMPONENTE — Indicadores de logro dentro de cada componente.
    Alineados al currículo nacional; baja frecuencia de cambio.
    """

    code = models.CharField(max_length=50, blank=True, db_index=True, verbose_name="Código")
    block_component = models.ForeignKey(
        "grading.BlockComponent",
        on_delete=models.CASCADE,
        related_name="indicators",
        verbose_name="Componente de Bloque",
    )
    name = models.CharField(max_length=200, verbose_name="Nombre")
    internal_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Ponderación Interna (%)",
        help_text="Peso del indicador dentro de su componente",
    )

    class Meta:
        app_label = "grading"
        verbose_name = "Indicador de Componente"
        verbose_name_plural = "Indicadores de Componente"
        ordering = ["block_component", "name"]

    def __str__(self):
        return f"{self.block_component.name} — {self.name}"
from django.db import models
from apps.core.models import TimeStampedModel


class EvaluationBlock(TimeStampedModel):
    """
    BLOQUE_EVALUACION — Bloques formativo/sumativo/diagnóstico por período académico.
    Se configura al inicio de cada período.
    """

    code = models.CharField(max_length=50, blank=True, db_index=True, verbose_name="Código")
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod",
        on_delete=models.CASCADE,
        related_name="evaluation_blocks",
        verbose_name="Período Académico",
    )
    subject_offering = models.ForeignKey(
        "academic.SubjectOffering",
        on_delete=models.CASCADE,
        related_name="evaluation_blocks",
        verbose_name="Oferta de Materia",
    )
    name = models.CharField(max_length=100, verbose_name="Nombre")
    evaluation_type = models.ForeignKey("grading.EvaluationType", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tipo de evaluación")
    weight_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Porcentaje de Ponderación",
        help_text="Porcentaje que representa este bloque en la nota final del período",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "grading"
        verbose_name = "Bloque de Evaluación"
        verbose_name_plural = "Bloques de Evaluación"
        ordering = ["academic_period", "subject_offering", "evaluation_type"]
        indexes = [
            models.Index(fields=["subject_offering", "academic_period"]),
        ]

    def __str__(self):
        return f"{self.academic_period.name} — {self.name} ({self.evaluation_type})"
from django.db import models
from apps.core.models import TimeStampedModel


class EvaluationType(TimeStampedModel):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "grading"
        verbose_name = "Tipo de Evaluación"
        verbose_name_plural = "Tipos de Evaluación"
        ordering = ["name"]

    def __str__(self):
        return self.name
from django.db import models
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class EvaluativeActivity(TimeStampedModel, SyncableModel):
    """
    ACTIVIDAD_EVALUATIVA — Tareas, lecciones, exámenes creados por el docente.
    Transaccional de alta frecuencia; creación continua durante el período.
    """

    component_indicator = models.ForeignKey(
        "grading.ComponentIndicator",
        on_delete=models.CASCADE,
        related_name="activities",
        verbose_name="Indicador de Componente",
    )
    teacher_subject_section = models.ForeignKey(
        "academic.TeacherSubjectSection",
        on_delete=models.CASCADE,
        related_name="evaluative_activities",
        verbose_name="Docente-Materia-Sección",
    )
    title = models.CharField(max_length=200, verbose_name="Título")
    activity_type = models.ForeignKey("grading.ActivityType", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tipo de Actividad")
    max_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Puntuación Máxima"
    )
    due_date = models.DateField(verbose_name="Fecha de Vencimiento")
    is_interdisciplinary_project = models.BooleanField(
        default=False,
        verbose_name="Es Proyecto Interdisciplinar",
        help_text="Indica si esta actividad forma parte de un proyecto interdisciplinar",
    )

    class Meta:
        app_label = "grading"
        verbose_name = "Actividad Evaluativa"
        verbose_name_plural = "Actividades Evaluativas"
        ordering = ["-due_date"]
        indexes = [
            models.Index(fields=["teacher_subject_section", "due_date"]),
            models.Index(fields=["component_indicator", "due_date"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.activity_type})"
from django.db import models
from apps.core.models import TimeStampedModel


class GradeChangeHistory(TimeStampedModel):
    student_note = models.ForeignKey(
        "grading.StudentNote",
        on_delete=models.CASCADE,
        related_name="change_history",
        verbose_name="Nota",
    )
    modified_by_user = models.ForeignKey(
        "iam.User",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Modificado por",
    )
    created_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="grade_changes_created", verbose_name="Creado por",
    )
    previous_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Nota Anterior"
    )
    new_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Nota Nueva"
    )
    previous_qualitative = models.ForeignKey(
        "grading.QualitativeScale",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="previous_grade_changes",
        verbose_name="Escala Cualitativa Anterior",
    )
    new_qualitative = models.ForeignKey(
        "grading.QualitativeScale",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="new_grade_changes",
        verbose_name="Nueva Escala Cualitativa",
    )
    reason = models.TextField(verbose_name="Razón del Cambio")
    reason_code = models.CharField(max_length=30, blank=True, verbose_name="Código de Razón")
    origin = models.CharField(max_length=20, choices=[
        ("MANUAL", "Manual"),
        ("RECOVERY", "Recuperación"),
        ("IMPORT", "Importación"),
        ("SYNC", "Sincronización"),
    ], default="MANUAL", verbose_name="Origen")
    device_origin = models.CharField(max_length=40, null=True, blank=True, verbose_name="Dispositivo de Origen")
    modified_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Modificado en"
    )

    class Meta:
        app_label = "grading"
        verbose_name = "Historial de Cambio de Calificación"
        verbose_name_plural = "Historiales de Cambio de Calificación"
        ordering = ["-modified_at"]
        indexes = [
            models.Index(fields=["student_note", "modified_at"]),
            models.Index(fields=["modified_by_user", "modified_at"]),
        ]

    def __str__(self):
        return f"{self.student_note} - {self.previous_score} → {self.new_score}"
from django.db import models
from apps.core.models import TimeStampedModel


class GradeType(TimeStampedModel):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    applicable_sublevels = models.ManyToManyField(
        "institutions.AcademicSublevel", blank=True, related_name="grade_types",
        verbose_name="Sublevels Aplicables",
    )

    class Meta:
        app_label = "grading"
        verbose_name = "Tipo de Calificación"
        verbose_name_plural = "Tipos de Calificación"
        ordering = ["name"]

    def __str__(self):
        return self.name
from django.db import models
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class LearningReport(TimeStampedModel, SyncableModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        verbose_name="Matrícula",
    )
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod",
        on_delete=models.CASCADE,
        verbose_name="Período Académico",
    )
    formative_avg = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Promedio Formativo",
    )
    summative_avg = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Promedio Sumativo",
    )
    final_avg = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Promedio Final",
    )
    attendance_rate = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Tasa de Asistencia",
    )
    behavior_scale = models.ForeignKey(
        "grading.QualitativeScale",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Escala de Conducta",
    )
    general_observations = models.TextField(null=True, blank=True, verbose_name="Observaciones generales")
    recommendations = models.TextField(null=True, blank=True, verbose_name="Recomendaciones")
    created_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True,
        related_name="created_reports", verbose_name="Creado por",
    )
    evaluated_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True,
        related_name="evaluated_reports", verbose_name="Evaluado por",
    )
    approved_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="approved_reports", verbose_name="Aprobado por",
    )
    is_final = models.BooleanField(default=False, verbose_name="Es definitivo")

    class Meta:
        app_label = "grading"
        verbose_name = "Informe de Aprendizaje"
        verbose_name_plural = "Informes de Aprendizaje"
        unique_together = [("enrollment", "academic_period")]
        ordering = ["-academic_period__start_date"]
        indexes = [
            models.Index(fields=["academic_period", "is_final"]),
        ]

    def __str__(self):
        return f"{self.enrollment} - {self.academic_period}"
from django.db import models
from apps.core.models import TimeStampedModel


class PeriodGradeSummary(TimeStampedModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="grade_summaries",
        verbose_name="Matrícula",
    )
    subject_offering = models.ForeignKey(
        "academic.SubjectOffering",
        on_delete=models.CASCADE,
        related_name="grade_summaries",
        verbose_name="Oferta de Asignatura",
    )
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod",
        on_delete=models.CASCADE,
        related_name="grade_summaries",
        verbose_name="Período Académico",
    )
    formative_avg = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Promedio Formativo"
    )
    summative_avg = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Promedio Sumativo"
    )
    final_avg_truncated = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Promedio Final Truncado"
    )
    qualitative_scale = models.ForeignKey(
        "grading.QualitativeScale",
        on_delete=models.PROTECT,
        null=True, blank=True,
        verbose_name="Escala Cualitativa",
    )
    requires_recovery = models.BooleanField(default=False, verbose_name="Requiere Recuperación")
    promotion_status = models.ForeignKey("grading.PromotionStatus", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Estado de Promoción")
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
        unique_together = ("enrollment", "subject_offering", "academic_period")
        indexes = [
            models.Index(fields=["academic_period", "subject_offering"]),
            models.Index(fields=["enrollment", "academic_period"]),
            models.Index(fields=["requires_recovery", "academic_period"]),
        ]

    def __str__(self):
        return f"{self.enrollment} - {self.subject_offering} ({self.academic_period})"
from django.db import models
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class ProjectNote(TimeStampedModel, SyncableModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="project_notes",
        verbose_name="Matrícula",
    )
    interdisciplinary_project = models.ForeignKey(
        "academic.InterdisciplinaryProject",
        on_delete=models.CASCADE,
        related_name="project_notes",
        verbose_name="Proyecto Interdisciplinario",
    )
    product_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Nota del producto"
    )
    presentation_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Nota de exposición"
    )
    final_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Nota final"
    )
    observation = models.TextField(null=True, blank=True, verbose_name="Observación")

    class Meta:
        app_label = "grading"
        verbose_name = "Nota de Proyecto"
        verbose_name_plural = "Notas de Proyectos"
        unique_together = ("enrollment", "interdisciplinary_project")
        indexes = [
            models.Index(fields=["interdisciplinary_project"]),
        ]

    def __str__(self):
        return f"{self.enrollment} - {self.interdisciplinary_project.title} ({self.final_score})"
from django.db import models
from apps.core.models import TimeStampedModel


class PromotionStatus(TimeStampedModel):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "grading"
        verbose_name = "Estado de Promoción"
        verbose_name_plural = "Estados de Promoción"
        ordering = ["name"]

    def __str__(self):
        return self.name
from django.db import models


class QualitativeScaleSublevel(models.Model):
    scale = models.ForeignKey(
        "grading.QualitativeScale",
        on_delete=models.CASCADE,
        related_name="sublevel_links",
        verbose_name="Escala Cualitativa",
    )
    sublevel = models.ForeignKey(
        "institutions.AcademicSublevel",
        on_delete=models.CASCADE,
        related_name="scale_links",
        verbose_name="Subnivel Académico",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "grading"
        verbose_name = "Escala Cualitativa por Subnivel"
        verbose_name_plural = "Escalas Cualitativas por Subnivel"
        unique_together = [("scale", "sublevel")]

    def __str__(self):
        return f"{self.scale.code} - {self.sublevel.name}"

from django.db import models
from apps.core.models import TimeStampedModel


class QualitativeScale(TimeStampedModel):
    code = models.CharField(max_length=10, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, blank=True, verbose_name="Nombre")
    description = models.TextField(verbose_name="Descripción")
    numeric_equivalence = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Equivalencia Numérica")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "grading"
        verbose_name = "Escala Cualitativa"
        verbose_name_plural = "Escalas Cualitativas"
        ordering = ["-numeric_equivalence"]

    def __str__(self):
        return f"{self.code} — {self.description}"
from django.db import models
from apps.core.models import TimeStampedModel


class RecoveryProcessHistory(TimeStampedModel):
    recovery_process = models.ForeignKey(
        "grading.RecoveryProcess",
        on_delete=models.CASCADE,
        verbose_name="Proceso de Recuperación",
    )
    action = models.CharField(max_length=30, choices=[
        ("STARTED", "Iniciado"),
        ("GRADE_UPDATED", "Calificación actualizada"),
        ("SESSION_COMPLETED", "Sesión completada"),
        ("COMPLETED", "Completado"),
        ("CANCELLED", "Cancelado"),
    ], verbose_name="Acción")
    previous_grade = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Calificación Anterior",
    )
    new_grade = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Nueva Calificación",
    )
    previous_status = models.ForeignKey(
        "grading.RecoveryProcessStatus",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="previous_recovery",
        verbose_name="Estado Anterior",
    )
    new_status = models.ForeignKey(
        "grading.RecoveryProcessStatus",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="new_recovery",
        verbose_name="Nuevo Estado",
    )
    notes = models.TextField(blank=True, verbose_name="Notas")
    changed_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True,
        verbose_name="Cambiado por",
    )

    class Meta:
        app_label = "grading"
        verbose_name = "Historial de Proceso de Recuperación"
        verbose_name_plural = "Historiales de Procesos de Recuperación"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recovery_process} - {self.action}"
from django.db import models


class RecoveryProcessStatus(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "grading"
        verbose_name = "Estado de Proceso de Recuperación"
        verbose_name_plural = "Estados de Procesos de Recuperación"
        ordering = ["name"]

    def __str__(self):
        return self.name
from django.db import models
from apps.core.models import TimeStampedModel


class RecoveryProcessType(TimeStampedModel):
    code = models.CharField(max_length=30, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    allows_improvement_eval = models.BooleanField(default=False, verbose_name="Permite evaluación de mejora")
    allows_suppletorio = models.BooleanField(default=False, verbose_name="Permite supletorio")
    min_grade_to_access = models.DecimalField(
        max_digits=4, decimal_places=2, default=7.00,
        verbose_name="Nota mínima para acceder",
    )
    max_recovery_attempts = models.IntegerField(default=1, verbose_name="Máximo de intentos")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "grading"
        verbose_name = "Tipo de Proceso de Recuperación"
        verbose_name_plural = "Tipos de Proceso de Recuperación"
        ordering = ["name"]

    def __str__(self):
        return self.name
from django.db import models
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class RecoveryProcess(TimeStampedModel, SyncableModel):
    period_grade_summary = models.ForeignKey(
        "grading.PeriodGradeSummary",
        on_delete=models.CASCADE,
        related_name="recovery_processes",
        verbose_name="Resumen de Calificaciones",
    )
    subject_offering = models.ForeignKey(
        "academic.SubjectOffering",
        on_delete=models.CASCADE,
        verbose_name="Oferta de Materia",
    )
    managed_by_user = models.ForeignKey(
        "iam.User",
        on_delete=models.CASCADE,
        related_name="recovery_processes",
        verbose_name="Gestionado por",
    )
    process_type = models.ForeignKey("grading.RecoveryProcessType", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tipo de proceso")
    initial_grade = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Nota Inicial")
    reinforcement_grade = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Nota de Refuerzo",
    )
    improvement_eval_grade = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Nota de Evaluación de Mejora",
    )
    final_calculated_grade = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Nota Final Calculada",
    )
    family_notified = models.BooleanField(default=False, verbose_name="Familia Notificada")
    family_notification_date = models.DateField(null=True, blank=True, verbose_name="Fecha de notificación familiar")
    start_date = models.DateField(verbose_name="Fecha de inicio")
    end_date = models.DateField(null=True, blank=True, verbose_name="Fecha de fin")
    reinforcement_plan = models.TextField(null=True, blank=True, verbose_name="Plan de refuerzo")
    objectives = models.TextField(null=True, blank=True, verbose_name="Objetivos")
    observations = models.TextField(null=True, blank=True, verbose_name="Observaciones")

    class Meta:
        app_label = "grading"
        verbose_name = "Proceso de Recuperación"
        verbose_name_plural = "Procesos de Recuperación"
        ordering = ["-start_date"]
        indexes = [
            models.Index(fields=["subject_offering", "start_date"]),
            models.Index(fields=["managed_by_user", "start_date"]),
        ]

    def __str__(self):
        return f"{self.period_grade_summary} - {self.process_type}"
from django.db import models
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class RecoverySession(TimeStampedModel, SyncableModel):
    recovery_process = models.ForeignKey(
        "grading.RecoveryProcess",
        on_delete=models.CASCADE,
        related_name="sessions",
        verbose_name="Proceso de Recuperación",
    )
    session_date = models.DateField(verbose_name="Fecha de la sesión")
    duration_minutes = models.IntegerField(default=60, verbose_name="Duración (minutos)")
    topics_covered = models.TextField(blank=True, verbose_name="Temas cubiertos")
    student_present = models.BooleanField(default=True, verbose_name="Estudiante presente")
    teacher_observation = models.TextField(null=True, blank=True, verbose_name="Observación del docente")

    class Meta:
        app_label = "grading"
        verbose_name = "Sesión de Refuerzo"
        verbose_name_plural = "Sesiones de Refuerzo"
        ordering = ["session_date"]

    def __str__(self):
        return f"Sesión {self.session_date} - {self.recovery_process}"
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class StudentNote(TimeStampedModel, SyncableModel):
    """
    NOTA_ACTIVIDAD — Calificación individual de un estudiante en una actividad.
    Entidad de mayor volumen; soporte offline-first.
    """

    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        verbose_name="Matrícula",
    )
    evaluative_activity = models.ForeignKey(
        "grading.EvaluativeActivity",
        on_delete=models.CASCADE,
        verbose_name="Actividad Evaluativa",
        null=True, blank=True,
    )
    grade_type = models.ForeignKey(
        "grading.GradeType",
        on_delete=models.PROTECT,
        verbose_name="Tipo de Calificación",
        null=True, blank=True,
    )
    grading_mode = models.CharField(
        max_length=20,
        choices=[
            ("NUMERIC", "Cuantitativa"),
            ("QUALITATIVE", "Cualitativa"),
        ],
        default="NUMERIC",
        verbose_name="Modo de Calificación",
        help_text="Define si la nota es numérica o cualitativa",
    )
    qualitative_scale = models.ForeignKey(
        "grading.QualitativeScale",
        on_delete=models.PROTECT,
        null=True, blank=True,
        verbose_name="Escala Cualitativa",
        help_text="Escala cualitativa equivalente a la nota (si aplica)",
    )
    numeric_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        verbose_name="Puntuación Numérica",
        help_text="Calificación numérica obtenida (escala 1-10)",
        null=True, blank=True,
    )
    manually_overridden = models.BooleanField(
        default=False, verbose_name="Anulada Manualmente"
    )
    teacher_observation = models.TextField(
        null=True, blank=True, verbose_name="Observación del Docente"
    )
    created_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="student_notes_created", verbose_name="Creado por",
    )
    modified_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="student_notes_modified", verbose_name="Modificado por",
    )

    class Meta:
        app_label = "grading"
        verbose_name = "Nota de Actividad"
        verbose_name_plural = "Notas de Actividades"
        unique_together = [("enrollment", "evaluative_activity")]
        indexes = [
            models.Index(fields=["enrollment", "evaluative_activity"]),
            models.Index(fields=["evaluative_activity", "numeric_score"]),
            models.Index(fields=["sync_status"]),
            models.Index(fields=["enrollment", "sync_status"]),
        ]

    def clean(self):
        super().clean()
        if self.grading_mode == "NUMERIC" and not self.numeric_score:
            raise ValidationError(
                {"numeric_score": "numeric_score es requerido para calificación cuantitativa"}
            )
        if self.grading_mode == "QUALITATIVE" and not self.qualitative_scale:
            raise ValidationError(
                {"qualitative_scale": "qualitative_scale es requerido para calificación cualitativa"}
            )
        if self.evaluative_activity_id and self.numeric_score is not None:
            max_value = self.evaluative_activity.max_score
            if self.numeric_score < 0 or self.numeric_score > max_value:
                raise ValidationError(
                    {"numeric_score": f"La nota debe estar entre 0 y {max_value}"}
                )

    def calculate_normalized_value(self):
        if not self.evaluative_activity_id:
            return self.numeric_score
        max_value = Decimal(self.evaluative_activity.max_score)
        if max_value == 0:
            return Decimal("0.00")
        normalized = (Decimal(self.numeric_score) / max_value) * Decimal("10")
        return normalized.quantize(Decimal("0.01"))

    def __str__(self):
        return f"{self.enrollment} - {self.evaluative_activity} (score: {self.numeric_score})"

-Iam
from django.db import models
from apps.core.models import TimeStampedModel


class Permission(TimeStampedModel):
    code = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Código del Permiso",
        help_text="Formato: '<app>.<acción>', ej: 'grading.create_note'",
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Descripción",
        help_text="Descripción legible del permiso",
    )
    module = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Módulo",
        help_text="Módulo asociado (grading, academic, etc)",
    )
    class Meta:
        app_label = "iam"
        verbose_name = "Permiso"
        verbose_name_plural = "Permisos"
        ordering = ["code"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["module"]),
        ]

    def __str__(self):
        return self.code
from django.db import models
from apps.core.models import TimeStampedModel


class RolePermission(TimeStampedModel):
    role = models.ForeignKey(
        "Role",
        on_delete=models.CASCADE,
        related_name="role_permissions",
        verbose_name="Rol",
        help_text="El rol que recibe el permiso",
    )
    permission = models.ForeignKey(
        "Permission",
        on_delete=models.CASCADE,
        related_name="permission_roles",
        verbose_name="Permiso",
        help_text="El permiso otorgado",
    )
    class Meta:
        app_label = "iam"
        verbose_name = "Permiso del Rol"
        verbose_name_plural = "Permisos del Rol"
        unique_together = ("role", "permission")
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["permission"]),
        ]

    def __str__(self):
        return f"{self.role.name} → {self.permission.code}"
from django.db import models
from apps.core.models import TimeStampedModel
from .permission import Permission


class Role(TimeStampedModel):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre del Rol",
        help_text="Nombre único del rol",
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Código del Rol",
        help_text="Código único del rol (DOCENTE, ADMIN, etc)",
        null=True,
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Descripción",
        help_text="Descripción del rol",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Indica si el rol puede ser asignado a nuevos usuarios",
    )
    class Meta:
        app_label = "iam"
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name

    def get_all_permissions(self):
        from .role_permission import RolePermission

        return Permission.objects.filter(permission_roles__role=self).distinct()
from django.db import models
from apps.core.models import TimeStampedModel


class UserRole(TimeStampedModel):
    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="user_roles",
        verbose_name="Usuario",
    )
    role = models.ForeignKey(
        "Role",
        on_delete=models.CASCADE,
        related_name="user_roles",
        verbose_name="Rol",
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Asignado en"
    )
    expires_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Expira en"
    )

    class Meta:
        app_label = "iam"
        verbose_name = "Rol del Usuario"
        verbose_name_plural = "Roles del Usuario"
        unique_together = ("user", "role")

    def __str__(self):
        return f"{self.user} → {self.role.name}"
import re
import unicodedata

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from apps.core.models import TimeStampedModel


class UserManager(BaseUserManager):
    def create_user(self, person, password=None, username=None, **extra_fields):
        if not person:
            raise ValueError("Person es obligatorio")
        email = self.normalize_email(person.email) if person.email else ""
        extra_fields.pop("user_type", None)
        if not username:
            username = User.generate_username(person.names, person.last_names)
        user = self.model(
            person=person, email=email, username=username, **extra_fields
        )
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, **fields):
        email = fields.get("email")
        if not email:
            raise ValueError("Email es obligatorio")
        username = fields.get("username") or email.split("@")[0]
        extra_fields = {k: v for k, v in fields.items() if k not in ["email", "username"]}
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        if fields.get("password"):
            user.set_password(fields["password"])
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, TimeStampedModel):
    person = models.OneToOneField(
        "people.Person",
        on_delete=models.CASCADE,
        null=True, blank=True,
        verbose_name="Persona",
    )
    username = models.CharField(
        max_length=50, unique=True, verbose_name="Nombre de Usuario",
    )
    email = models.EmailField(
        unique=True, verbose_name="Correo Electrónico",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    is_staff = models.BooleanField(default=False, verbose_name="Es Personal del Admin")
    is_superuser = models.BooleanField(default=False, verbose_name="Es Superusuario")

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        app_label = "iam"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["id"]
        indexes = [
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        if self.person:
            return f"{self.person.names} {self.person.last_names} ({self.username})"
        return f"User #{self.pk}"

    @staticmethod
    def _normalize(text):
        text = text.lower().strip()
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
        text = re.sub(r"[^a-z0-9]", "", text)
        return text

    @staticmethod
    def generate_username(names, last_names):
        if not names or not last_names:
            return None
        first_name = User._normalize(names.split()[0])
        first_last_name = User._normalize(last_names.split()[0])
        base_username = first_name[0] + first_last_name
        if not User.objects.filter(username=base_username).exists():
            return base_username
        existing = User.objects.filter(username__startswith=base_username).values_list("username", flat=True)
        max_num = 1
        for uname in existing:
            match = re.match(r"^" + re.escape(base_username) + r"(\d+)$", uname)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
        return f"{base_username}{max_num + 1:02d}"

    def has_perm(self, permission_code):
        if self.is_superuser:
            return True
        return self.user_roles.filter(role__role_permissions__permission__code=permission_code).exists()

    def has_module_perms(self, app_label):
        if self.is_superuser:
            return True
        return False

    def get_all_permissions(self):
        return set(self.user_roles.values_list("role__role_permissions__permission__code", flat=True).distinct())

    @property
    def user_category(self):
        role = self.user_roles.select_related("role").first()
        if not role:
            return "SIN_ROL"
        code = role.role.code
        if code in ("ESTUDIANTE",):
            return "ESTUDIANTE"
        if code in ("REPRESENTANTE",):
            return "REPRESENTANTE"
        if code in ("DOCENTE", "DIRECTOR", "CONSEJERO", "RECTOR"):
            return "DOCENTE"
        if code in ("ADMIN",):
            return "ADMIN"
        return "OTRO"

-Instituciones
from django.db import models
from apps.core.models import TimeStampedModel


class AcademicGrade(TimeStampedModel):
    code = models.CharField(max_length=50, blank=True, db_index=True, verbose_name="Código")
    academic_sublevel = models.ForeignKey(
        "institutions.AcademicSublevel",
        on_delete=models.PROTECT,
        verbose_name="Subnivel Académico",
        null=True, blank=True,
    )
    name = models.CharField(max_length=100, verbose_name="Nombre del Grado")
    sequence_order = models.IntegerField(verbose_name="Orden")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "institutions"
        verbose_name = "Grado Académico"
        verbose_name_plural = "Grados Académicos"
        ordering = ["sequence_order"]

    def __str__(self):
        return f"{self.name}"

    @property
    def academic_level(self):
        if self.academic_sublevel:
            return self.academic_sublevel.academic_level
        return None
from django.db import models
from apps.core.models import TimeStampedModel


class AcademicLevel(TimeStampedModel):
    code = models.CharField(max_length=50, blank=True, db_index=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre del Nivel")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "institutions"
        verbose_name = "Nivel Académico"
        verbose_name_plural = "Niveles Académicos"
        ordering = ["name"]

    def __str__(self):
        return self.name
from django.db import models
from apps.core.models import TimeStampedModel


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
        return f"{self.academic_level.name} - {self.name}"
from django.db import models
from apps.core.models import TimeStampedModel


class SchoolYear(TimeStampedModel):
    name = models.CharField(max_length=255, verbose_name="Nombre del Año Escolar")
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    end_date = models.DateField(verbose_name="Fecha de Fin")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    class Meta:
        app_label = "institutions"
        verbose_name = "Año Escolar"
        verbose_name_plural = "Años Escolares"

    def __str__(self):
        return f"{self.name} - {self.start_date} - {self.end_date}"

from django.db import models
from apps.core.models import TimeStampedModel


class Section(TimeStampedModel):
    code = models.CharField(max_length=50, blank=True, db_index=True, verbose_name="Código")
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
            return (
                f"{self.school_year.name} - {self.academic_grade.name} {self.parallel}"
            )
        return f"{self.school_year.name} - {self.parallel}"

-Integracion:
from django.db import models
from apps.core.models import TimeStampedModel


class SyncOperation(TimeStampedModel):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "integration"
        verbose_name = "Operación de Sincronización"
        verbose_name_plural = "Operaciones de Sincronización"
        ordering = ["name"]

    def __str__(self):
        return self.name
import uuid
import hashlib
from django.db import models
from apps.core.models import TimeStampedModel


class SyncQueue(TimeStampedModel):
    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID",
    )
    idempotency_key = models.CharField(
        max_length=64, unique=True, db_index=True, blank=True, verbose_name="Clave de Idempotencia",
    )
    user = models.ForeignKey(
        "iam.User",
        on_delete=models.CASCADE,
        verbose_name="Usuario origen",
    )
    source_table = models.CharField(
        max_length=100, verbose_name="Tabla Origen",
    )
    record_uuid = models.CharField(
        max_length=36, verbose_name="UUID del Registro",
    )
    operation = models.ForeignKey("integration.SyncOperation", on_delete=models.PROTECT, verbose_name="Operación")
    payload = models.JSONField(
        verbose_name="Payload", default=dict, blank=True,
    )
    previous_state = models.JSONField(
        default=dict, blank=True, verbose_name="Estado Anterior",
    )
    attempts = models.PositiveIntegerField(default=0, verbose_name="Intentos")
    max_attempts = models.PositiveIntegerField(default=5, verbose_name="Máximo de Intentos")
    last_error = models.TextField(null=True, blank=True, verbose_name="Último Error")
    last_attempt_at = models.DateTimeField(null=True, blank=True, verbose_name="Último Intento")
    status = models.ForeignKey("integration.SyncStatus", on_delete=models.PROTECT, null=True, blank=True, verbose_name="Estado")
    conflict_detected = models.BooleanField(default=False, verbose_name="Conflicto Detectado")
    resolution_strategy = models.CharField(max_length=30, null=True, blank=True, verbose_name="Estrategia de Resolución")
    processed_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="sync_processed", verbose_name="Procesado por",
    )
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="Procesada en")
    resolved_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="sync_resolved", verbose_name="Resuelto por",
    )
    resolution_notes = models.TextField(null=True, blank=True, verbose_name="Notas de resolución")

    class Meta:
        app_label = "integration"
        verbose_name = "Cola de Sincronización"
        verbose_name_plural = "Cola de Sincronización"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["source_table", "record_uuid"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["conflict_detected", "status"]),
        ]

    def save(self, *args, **kwargs):
        if not self.idempotency_key:
            op_code = self.operation.code if self.operation else "UNKNOWN"
            raw = f"{self.source_table}:{self.record_uuid}:{op_code}:{self.attempts}"
            self.idempotency_key = hashlib.sha256(raw.encode()).hexdigest()[:64]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.operation} — {self.source_table} ({self.status})"
from django.db import models
from apps.core.models import TimeStampedModel


class SyncSchemaVersion(TimeStampedModel):
    model_name = models.CharField(max_length=100, unique=True, verbose_name="Nombre del modelo")
    schema_version = models.PositiveIntegerField(default=1, verbose_name="Versión del esquema")
    fields_hash = models.CharField(max_length=64, verbose_name="Hash de campos")
    min_client_version = models.CharField(max_length=20, default="1.0.0", verbose_name="Versión mínima de cliente")

    class Meta:
        app_label = "integration"
        verbose_name = "Versión de Esquema de Sincronización"
        verbose_name_plural = "Versiones de Esquema de Sincronización"
        ordering = ["model_name"]

    def __str__(self):
        return f"{self.model_name} v{self.schema_version}"
from django.db import models
from apps.core.models import TimeStampedModel


class SyncStatus(TimeStampedModel):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "integration"
        verbose_name = "Estado de Sincronización"
        verbose_name_plural = "Estados de Sincronización"
        ordering = ["name"]

    def __str__(self):
        return self.name
import uuid
from django.db import models
from django.db.models import F
from django.utils import timezone


class SyncStatusChoices(models.TextChoices):
    PENDING = "PENDING", "Pendiente de sincronizar"
    PROCESSING = "PROCESSING", "En procesamiento"
    SYNCED = "SYNCED", "Sincronizado"
    ERROR = "ERROR", "Error de sincronización"
    CONFLICT = "CONFLICT", "Conflicto detectado"


class SyncableModel(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, verbose_name="UUID")
    sync_status = models.CharField(
        max_length=20,
        choices=SyncStatusChoices.choices,
        default=SyncStatusChoices.PENDING,
        db_index=True,
        verbose_name="Estado de Sincronización",
    )
    sync_version = models.PositiveIntegerField(default=1, verbose_name="Versión de Sincronización")
    synced_at = models.DateTimeField(null=True, blank=True, verbose_name="Sincronizado en")
    device_origin = models.CharField(max_length=40, null=True, blank=True, verbose_name="Dispositivo de Origen")
    conflict_resolved = models.BooleanField(default=False, verbose_name="Conflicto Resuelto")
    conflict_notes = models.TextField(null=True, blank=True, verbose_name="Notas de Conflicto")

    class Meta:
        abstract = True

    def increment_sync_version(self):
        self.sync_version = F("sync_version") + 1

    def mark_synced(self):
        self.sync_status = SyncStatusChoices.SYNCED
        self.synced_at = timezone.now()

    def mark_conflict(self):
        self.sync_status = SyncStatusChoices.CONFLICT

    def mark_error(self):
        self.sync_status = SyncStatusChoices.ERROR

-People
from django.db import models
from apps.core.models import TimeStampedModel


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
from django.db import models
from django.utils import timezone
from apps.core.models import TimeStampedModel


class Person(TimeStampedModel):
    document_type = models.ForeignKey(
        "people.DocumentType",
        on_delete=models.PROTECT,
        verbose_name="Tipo de Documento",
        null=True,
    )
    document_number = models.CharField(
        max_length=20, unique=True, verbose_name="Número de Documento"
    )
    names = models.CharField(max_length=100, verbose_name="Nombres")
    last_names = models.CharField(max_length=100, verbose_name="Apellidos")
    birth_date = models.DateField(
        null=True, blank=True, verbose_name="Fecha de Nacimiento"
    )
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
-Students
from django.db import models
from apps.core.models import TimeStampedModel


class EnrollmentHistory(TimeStampedModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        verbose_name="Matrícula",
    )
    previous_status = models.ForeignKey(
        "students.EnrollmentStatus",
        on_delete=models.PROTECT,
        related_name="previous_enrollments",
        verbose_name="Estado Anterior",
    )
    new_status = models.ForeignKey(
        "students.EnrollmentStatus",
        on_delete=models.PROTECT,
        related_name="new_enrollments",
        verbose_name="Nuevo Estado",
    )
    changed_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True,
        verbose_name="Cambiado por",
    )
    change_reason = models.TextField(blank=True, verbose_name="Razón del cambio")
    effective_date = models.DateField(verbose_name="Fecha efectiva")

    class Meta:
        app_label = "students"
        verbose_name = "Historial de Matrícula"
        verbose_name_plural = "Historiales de Matrícula"
        ordering = ["-effective_date"]

    def __str__(self):
        return f"{self.enrollment}: {self.previous_status} → {self.new_status} ({self.effective_date})"
from django.db import models
from apps.core.models import TimeStampedModel


class EnrollmentStatus(TimeStampedModel):
    code = models.CharField(max_length=10, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "students"
        verbose_name = "Estado de Matrícula"
        verbose_name_plural = "Estados de Matrícula"
        ordering = ["name"]

    def __str__(self):
        return self.name
from django.db import models
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class Enrollment(TimeStampedModel, SyncableModel):
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Estudiante",
    )
    section = models.ForeignKey(
        "institutions.Section",
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Sección",
    )
    school_year = models.ForeignKey(
        "institutions.SchoolYear",
        on_delete=models.CASCADE,
        verbose_name="Año Escolar",
    )
    enrollment_status = models.ForeignKey(
        "students.EnrollmentStatus",
        on_delete=models.PROTECT,
        verbose_name="Estado de Matrícula",
    )
    enrollment_date = models.DateField(
        verbose_name="Fecha de Matrícula",
        auto_now_add=True,
    )
    withdrawal_date = models.DateField(
        null=True, blank=True, verbose_name="Fecha de Retiro"
    )
    withdrawal_reason = models.ForeignKey(
        "students.WithdrawalReason",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Motivo de Retiro",
    )
    is_repeat = models.BooleanField(default=False, verbose_name="Es repitente")
    repeated_school_year = models.ForeignKey(
        "institutions.SchoolYear",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="repeated_enrollments",
        verbose_name="Año escolar repetido",
    )
    created_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="enrollments_created", verbose_name="Creado por",
    )
    approved_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="enrollments_approved", verbose_name="Aprobado por",
    )

    class Meta:
        app_label = "students"
        verbose_name = "Matrícula"
        verbose_name_plural = "Matrículas"
        unique_together = (("student", "section", "school_year"),)
        indexes = [
            models.Index(fields=["student", "enrollment_status"]),
            models.Index(fields=["section", "enrollment_status"]),
            models.Index(fields=["school_year", "enrollment_status"]),
            models.Index(fields=["student", "school_year"]),
        ]

    def __str__(self):
        return f"{self.student} - {self.section} ({self.enrollment_status})"

    def save(self, *args, **kwargs):
        if not hasattr(self, "school_year") or self.school_year is None:
            if self.section and hasattr(self.section, "school_year") and self.section.school_year:
                self.school_year = self.section.school_year
        super().save(*args, **kwargs)
from django.db import models


class Kinship(models.Model):
    code = models.CharField(max_length=30, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "students"
        verbose_name = "Parentesco"
        verbose_name_plural = "Parentescos"
        ordering = ["name"]

    def __str__(self):
        return self.name
from django.db import models


class ResidentialZone(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "students"
        verbose_name = "Zona Residencial"
        verbose_name_plural = "Zonas Residenciales"
        ordering = ["name"]

    def __str__(self):
        return self.name
from django.db import models


class SpecialNeedsType(models.Model):
    code = models.CharField(max_length=30, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "students"
        verbose_name = "Tipo de Necesidad Especial"
        verbose_name_plural = "Tipos de Necesidades Especiales"
        ordering = ["name"]

    def __str__(self):
        return self.name

from django.db import models
from apps.core.models import TimeStampedModel


class StudentRepresentative(TimeStampedModel):
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="representatives_set",
        verbose_name="Estudiante",
    )
    person = models.ForeignKey(
        "people.Person",
        on_delete=models.CASCADE,
        related_name="student_representatives",
        null=True, blank=True,
        verbose_name="Persona",
    )
    kinship = models.ForeignKey(
        "students.Kinship",
        on_delete=models.PROTECT,
        verbose_name="Parentesco",
    )
    is_primary = models.BooleanField(default=False, verbose_name="Es Principal")
    can_pickup = models.BooleanField(default=True, verbose_name="Puede Recoger")
    emergency_contact = models.BooleanField(default=False, verbose_name="Contacto de Emergencia")
    receives_notifications = models.BooleanField(default=True, verbose_name="Recibe Notificaciones")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    class Meta:
        app_label = "students"
        verbose_name = "Relación Estudiante-Representante"
        verbose_name_plural = "Relaciones Estudiante-Representante"
        unique_together = ("student", "person")
        ordering = ["-is_primary", "-created_at"]

    def __str__(self):
        return f"{self.student} - {self.person.get_full_name()}"

from django.db import models
from apps.core.models import TimeStampedModel


class Student(TimeStampedModel):
    person = models.OneToOneField(
        "people.Person",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Persona",
    )
    student_code = models.CharField(
        max_length=50, unique=True, verbose_name="Código de Estudiante"
    )
    residential_zone = models.ForeignKey(
        "students.ResidentialZone",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Zona Residencial",
    )
    distance_to_school_km = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Distancia al Colegio (km)",
    )
    has_special_needs = models.BooleanField(
        default=False, verbose_name="Tiene Necesidades Educativas Especiales (NEE)"
    )
    special_needs_type = models.ForeignKey(
        "students.SpecialNeedsType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tipo de NEE",
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
        if self.person:
            return self.person.get_full_name()
        return f"Student #{self.pk}"

    def get_full_name(self):
        if self.person:
            return self.person.get_full_name()
        return ""

    def get_age(self):
        from datetime import date

        if self.person and self.person.birth_date:
            today = date.today()
            return (
                today.year
                - self.person.birth_date.year
                - (
                    (today.month, today.day)
                    < (self.person.birth_date.month, self.person.birth_date.day)
                )
            )
        return 0

from django.db import models


class WithdrawalReason(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "students"
        verbose_name = "Motivo de Retiro"
        verbose_name_plural = "Motivos de Retiro"
        ordering = ["name"]

    def __str__(self):
        return self.name