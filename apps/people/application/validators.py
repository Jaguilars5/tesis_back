def validate_required_fields_city(**kwargs):
    errors = {}
    for field in ["name", "code"]:
        value = kwargs.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors[field] = f"{field} es obligatorio"
    return errors


def validate_code_format(code):
    if code and not code.strip():
        return {"code": "El codigo no puede estar vacio"}
    return {}


def run_all_validators_city(**kwargs):
    errors = {}
    errors.update(validate_required_fields_city(**kwargs))
    errors.update(validate_code_format(kwargs.get("code")))
    return errors


def validate_required_fields_document_type(**kwargs):
    errors = {}
    for field in ["code", "name"]:
        value = kwargs.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors[field] = f"{field} es obligatorio"
    return errors


def run_all_validators_document_type(**kwargs):
    errors = {}
    errors.update(validate_required_fields_document_type(**kwargs))
    errors.update(validate_code_format(kwargs.get("code")))
    return errors


def validate_required_fields_person(**kwargs):
    errors = {}
    for field in ["names", "last_names"]:
        value = kwargs.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors[field] = f"{field} es obligatorio"
    return errors


def validate_document_number(value):
    if value and len(value) < 5:
        return {"document_number": "El numero de documento debe tener al menos 5 caracteres"}
    return {}


def validate_required_fields_parish(**kwargs):
    errors = {}
    for field in ["name", "code", "parish_type", "city_id"]:
        value = kwargs.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors[field] = f"{field} es obligatorio"
    valid_types = ["URBANA", "RURAL"]
    ptype = kwargs.get("parish_type")
    if ptype and ptype not in valid_types:
        errors["parish_type"] = f"Tipo inválido: debe ser URBANA o RURAL"
    return errors


def run_all_validators_parish(**kwargs):
    errors = {}
    errors.update(validate_required_fields_parish(**kwargs))
    errors.update(validate_code_format(kwargs.get("code")))
    return errors


def run_all_validators_person(**kwargs):
    errors = {}
    errors.update(validate_required_fields_person(**kwargs))
    errors.update(validate_document_number(kwargs.get("document_number")))
    return errors
