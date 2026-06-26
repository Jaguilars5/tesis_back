def validate_name_not_empty(name):
    if not name or not str(name).strip():
        return {"name": "El nombre del grado es obligatorio"}
    return {}


def run_all_validators(**kwargs):
    errors = {}
    errors.update(validate_name_not_empty(kwargs.get("name", "")))
    return errors
