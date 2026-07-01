"""Re-encola items de la cola de sincronización que quedaron atascados.

Útil cuando items terminaron en ERROR/PROCESSING (por ejemplo, por un bug ya
corregido) y no se reprocesan solos porque la tarea omite items que no están en
PENDING. Resetea los items seleccionados a PENDING (attempts=0) y los despacha
de nuevo al worker de Celery.

Ejemplos:
    python manage.py reprocess_sync_queue                 # todos los ERROR
    python manage.py reprocess_sync_queue --status ERROR,PROCESSING
    python manage.py reprocess_sync_queue --id 11 12
    python manage.py reprocess_sync_queue --dry-run
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.integration.infrastructure.models import SyncStatusChoices
from apps.integration.infrastructure.repositories import SyncQueueRepository


VALID_STATUSES = {
    SyncStatusChoices.PENDING,
    SyncStatusChoices.PROCESSING,
    SyncStatusChoices.ERROR,
    SyncStatusChoices.CONFLICT,
}


class Command(BaseCommand):
    help = "Re-encola items atascados de SyncQueue (los resetea a PENDING y los despacha)."
    # Evita el system check que importa toda la URLconf (lento e innecesario aqui).
    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument(
            "--status",
            default="ERROR",
            help="Estados a reprocesar, separados por coma. Default: ERROR. "
                 "(ERROR, PROCESSING, CONFLICT, PENDING)",
        )
        parser.add_argument(
            "--id",
            nargs="+",
            type=int,
            default=None,
            help="IDs específicos a reprocesar (ignora --status).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Solo muestra qué items se reprocesarían, sin tocar nada.",
        )

    def handle(self, *args, **options):
        from apps.integration.tasks.sync_tasks import process_sync_queue_item

        ids = options.get("id")
        dry_run = options.get("dry_run")

        if ids:
            items = [SyncQueueRepository.get_by_id(pk) for pk in ids]
            items = [item for item in items if item is not None]
            missing = set(ids) - {item.id for item in items}
            for pk in sorted(missing):
                self.stdout.write(self.style.WARNING(f"  - id={pk} no encontrado, se omite"))
        else:
            statuses = [s.strip().upper() for s in options["status"].split(",") if s.strip()]
            invalid = [s for s in statuses if s not in VALID_STATUSES]
            if invalid:
                self.stderr.write(self.style.ERROR(f"Estados inválidos: {invalid}. Válidos: {sorted(VALID_STATUSES)}"))
                return
            items = list(SyncQueueRepository.filter(status__in=statuses).order_by("created_at"))

        if not items:
            self.stdout.write(self.style.WARNING("No hay items que reprocesar."))
            return

        self.stdout.write(f"Se reprocesarán {len(items)} item(s):")
        for item in items:
            self.stdout.write(
                f"  - id={item.id} source_table={item.source_table!r} "
                f"operation={item.operation!r} record_uuid={item.record_uuid!r} "
                f"status={item.status} attempts={item.attempts}"
            )

        if dry_run:
            self.stdout.write(self.style.SUCCESS("[dry-run] No se realizó ningún cambio."))
            return

        dispatched = 0
        for item in items:
            SyncQueueRepository.update(
                item.id,
                status=SyncStatusChoices.PENDING,
                attempts=0,
                last_error="",
                last_attempt_at=timezone.now(),
            )
            process_sync_queue_item.delay(item.id)
            dispatched += 1

        self.stdout.write(self.style.SUCCESS(
            f"Listo: {dispatched} item(s) reseteados a PENDING y despachados a Celery."
        ))
