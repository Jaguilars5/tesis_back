from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ...services.sync_service import SyncQueueService, IncompatibleSchemaError
from ...repositories.sync_status_repository import SyncStatusRepository
from django.utils import timezone


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def sync_push(request):
    operations = request.data.get("operations", [])
    results = []
    accepted = 0
    rejected = 0
    conflicts = 0

    for op in operations:
        try:
            source_table = op.get("source_table")
            operation_code = op.get("operation")
            record_uuid = op.get("record_uuid")
            payload = op.get("payload", {})
            client_version = op.get("client_version")

            from ...models import SyncOperation
            sync_op, _ = SyncOperation.objects.get_or_create(
                code=operation_code,
                defaults={"name": operation_code.capitalize()},
            )

            result = SyncQueueService.queue_operation(
                user=request.user,
                source_table=source_table,
                record_uuid=record_uuid,
                operation=sync_op,
                payload=payload,
                client_version=client_version,
            )

            if result is None:
                accepted += 1
                results.append({
                    "record_uuid": record_uuid,
                    "status": "SYNCED",
                    "server_version": 1,
                })
            elif hasattr(result, "id"):
                accepted += 1
                results.append({
                    "record_uuid": record_uuid,
                    "status": "QUEUED",
                    "queue_id": result.id,
                })
            else:
                rejected += 1
                results.append({
                    "record_uuid": record_uuid,
                    "status": "REJECTED",
                    "message": str(result),
                })

        except IncompatibleSchemaError as e:
            rejected += 1
            results.append({
                "record_uuid": record_uuid,
                "status": "INCOMPATIBLE",
                "message": str(e),
            })
        except Exception as e:
            rejected += 1
            results.append({
                "record_uuid": record_uuid,
                "status": "ERROR",
                "message": str(e),
            })

    return Response({
        "ok": True,
        "data": {
            "accepted": accepted,
            "rejected": rejected,
            "conflicts": conflicts,
            "results": results,
        },
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def sync_pull(request):
    since = request.query_params.get("since")
    source_table = request.query_params.get("source_table")

    from ...models import SyncQueue
    qs = SyncQueue.objects.all()

    if since:
        from django.utils.dateparse import parse_datetime
        dt = parse_datetime(since)
        if dt:
            qs = qs.filter(processed_at__gte=dt)

    if source_table:
        qs = qs.filter(source_table=source_table)

    qs = qs.order_by("-created_at")[:100]

    results = []
    for item in qs:
        results.append({
            "uuid": str(item.uuid),
            "source_table": item.source_table,
            "operation": item.operation.code if item.operation else None,
            "record_uuid": item.record_uuid,
            "payload": item.payload,
            "status": item.status.code if item.status else None,
            "processed_at": item.processed_at.isoformat() if item.processed_at else None,
        })

    return Response({
        "ok": True,
        "data": {
            "count": len(results),
            "results": results,
        },
    })
