from django.db import models


class GradeChangeHistory(models.Model):
    student_note = models.ForeignKey(
        "grading.StudentNote",
        on_delete=models.CASCADE,
        related_name="change_history",
        verbose_name="Nota",
    )
    modified_by_user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Modificado por",
    )
    previous_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Nota Anterior"
    )
    new_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Nota Nueva"
    )
    reason = models.TextField(verbose_name="Razón del Cambio")
    modified_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Modificado en"
    )

    class Meta:
        app_label = "grading"
        verbose_name = "Historial de Cambio de Nota"
        verbose_name_plural = "Historial de Cambios de Notas"
        ordering = ["-modified_at"]

    def __str__(self):
        return f"{self.student_note} - {self.previous_score} → {self.new_score}"
