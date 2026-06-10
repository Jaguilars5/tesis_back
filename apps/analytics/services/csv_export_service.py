import csv
import io
from django.apps import apps


class CSVExportService:

    EXPORT_TYPES = {
        "risk": {
            "model": "StudentRiskScore",
            "fields": ["enrollment__student__student_code", "risk_score", "risk_label"],
            "headers": ["Código Estudiante", "Score Riesgo", "Nivel"],
        },
        "attendance": {
            "model": "StudentFeatureSnapshot",
            "fields": ["enrollment__student__student_code", "attendance_rate", "tardiness_count"],
            "headers": ["Código Estudiante", "% Asistencia", "Tardanzas"],
        },
    }

    @classmethod
    def generate_csv(cls, export_type, academic_period_id):
        config = cls.EXPORT_TYPES.get(export_type)
        if not config:
            raise ValueError(f"Tipo de exportación no válido: {export_type}")

        queryset = (
            apps.get_model("analytics", config["model"])
            .objects.filter(academic_period_id=academic_period_id)
            .values_list(*config["fields"])
        )

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(config["headers"])

        for row in queryset:
            writer.writerow(row)

        return output.getvalue()
