def validate_parallel_not_empty(parallel):
    if not parallel or not str(parallel).strip():
        return {"parallel": "El paralelo es obligatorio"}
    return {}


def run_all_validators(**kwargs):
    errors = {}
    errors.update(validate_parallel_not_empty(kwargs.get("parallel", "")))
    return errors
