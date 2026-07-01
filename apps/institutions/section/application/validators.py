def validate_parallel_not_empty(parallel):
    if not parallel or not str(parallel).strip():
        return {"parallel": "El paralelo es obligatorio"}
    return {}


def validate_code_not_empty(code):
    if not code or not str(code).strip():
        return {"code": "El código es obligatorio"}
    return {}


def validate_capacity_required(capacity):
    if not capacity or int(capacity) < 1:
        return {"capacity": "La capacidad es obligatoria"}
    return {}


def validate_school_year_required(school_year):
    if not school_year:
        return {"school_year": "El año escolar es obligatorio"}
    return {}


def validate_academic_grade_required(academic_grade):
    if not academic_grade:
        return {"academic_grade": "El grado académico es obligatorio"}
    return {}


def run_all_validators(**kwargs):
    errors = {}
    errors.update(validate_parallel_not_empty(kwargs.get("parallel", "")))
    return errors
