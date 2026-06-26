"""
Validaciones de negocio para SyncQueue.
"""

from ..infrastructure.models import SyncOperationChoices


def validate_source_table(value):
    if not value or not isinstance(value, str) or not value.strip():
        return {"source_table": "source_table es obligatorio"}
    return {}


def validate_record_uuid(value):
    if not value:
        return {"record_uuid": "record_uuid es obligatorio"}
    return {}


def validate_operation(value):
    valid_ops = [c for c, _ in SyncOperationChoices.choices]
    if value not in valid_ops:
        return {"operation": f"operation debe ser uno de: {', '.join(valid_ops)}"}
    return {}


def validate_push_operation(op):
    errors = {}
    errors.update(validate_source_table(op.get("source_table")))
    errors.update(validate_record_uuid(op.get("record_uuid")))
    errors.update(validate_operation(op.get("operation")))
    return errors


def run_all_validators(**kwargs):
    errors = {}
    errors.update(validate_source_table(kwargs.get("source_table")))
    errors.update(validate_record_uuid(kwargs.get("record_uuid")))
    errors.update(validate_operation(kwargs.get("operation")))
    return errors
