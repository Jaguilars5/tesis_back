"""
Validaciones de negocio para AbsenceType.

Cada función validadora recibe los datos necesarios y retorna un dict
{field: mensaje} si la regla se viola, o un dict vacío si pasa.

Las funciones son PURAS: no mutan estado, no escriben a la DB.
El service las orquesta y acumula los errores.
"""

from ..infrastructure.repositories import AbsenceTypeRepository


def validate_required_fields(data, required):
    """Verifica que los campos obligatorios estén presentes y no vacíos."""
    errors = {}
    for field in required:
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors[field] = f"{field} es obligatorio"
    return errors


def validate_unique_code(code, exclude_id=None):
    """El código debe ser único entre los tipos de ausencia."""
    if code is None:
        return {}
    if AbsenceTypeRepository.code_exists(code, exclude_id=exclude_id):
        return {"code": f"Ya existe un tipo de ausencia con el código '{code}'"}
    return {}


def run_all_validators(code=None, name=None, exclude_id=None, partial=False):
    """
    Ejecuta todas las validaciones y acumula los errores en un solo dict.

    - En creación (`partial=False`) se exigen los campos obligatorios.
    - En actualización (`partial=True`) solo se validan los campos provistos.
    """
    errors = {}
    if not partial:
        errors.update(
            validate_required_fields({"code": code, "name": name}, ["code", "name"])
        )
    errors.update(validate_unique_code(code, exclude_id=exclude_id))
    return errors
