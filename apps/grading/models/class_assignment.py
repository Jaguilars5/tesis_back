from django.db import models


class ClassAssignment(models.Model):
    evaluation_subcriteria = models.ForeignKey(
        "grading.EvaluationSubcriteria",
        on_delete=models.CASCADE,
        related_name="assignments",
        verbose_name="Subcriterio de Evaluación",
    )
    teacher_subject_section = models.ForeignKey(
        "academic.Teacher_Subject_Section",
        on_delete=models.CASCADE,
        related_name="assignments",
        verbose_name="Docente-Materia-Sección",
    )
    title = models.CharField(max_length=200, verbose_name="Título")
    max_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Puntaje Máximo"
    )
    due_date = models.DateField(verbose_name="Fecha de Entrega")

    class Meta:
        app_label = "grading"
        verbose_name = "Tarea/Actividad"
        verbose_name_plural = "Tareas/Actividades"
        ordering = ["-due_date"]

    def __str__(self):
        return self.title
