import logging

from django.db import transaction

from apps.attendance.models import Attendance
from apps.integration.tasks.sync_tasks import BaseSyncHandler, register_sync_handler

logger = logging.getLogger(__name__)


@register_sync_handler("attendance")
class AttendanceSyncHandler(BaseSyncHandler):
    model = Attendance
