"""
Validaciones de negocio para ConductIncident.
"""


def validate_required_fields(data, required):
    errors = {}
    for field in required:
        if field not in data or data[field] is None:
            errors[field] = f"{field} es obligatorio"
        elif isinstance(data[field], str) and not data[field].strip():
            errors[field] = f"{field} no puede estar vacío"
    return errors


def run_all_validators(**kwargs):
    errors = {}
    errors.update(validate_required_fields(kwargs, [
        "incident_type_id", "severity_id", "academic_period_id",
        "enrollment_id", "incident_date",
    ]))
    return errors
