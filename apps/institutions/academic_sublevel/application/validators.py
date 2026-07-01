def validate_name_not_empty(name):
    if not name or not str(name).strip():
        return {"name": "El nombre del subnivel es obligatorio"}
    return {}


def validate_code_not_empty(code):
    if not code or not str(code).strip():
        return {"code": "El código del subnivel es obligatorio"}
    return {}


def validate_academic_level_required(academic_level_id):
    if not academic_level_id:
        return {"academic_level": "El nivel académico es obligatorio"}
    return {}


def run_all_validators(**kwargs):
    errors = {}
    errors.update(validate_name_not_empty(kwargs.get("name", "")))
    return errors
