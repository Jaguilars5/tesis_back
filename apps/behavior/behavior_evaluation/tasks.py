from .infrastructure.models import BehaviorEvaluation
from apps.integration.tasks.sync_tasks import BaseSyncHandler, register_sync_handler


@register_sync_handler("behavior_evaluation")
class BehaviorEvaluationSyncHandler(BaseSyncHandler):
    source_table = "behavior_evaluation"
    model = BehaviorEvaluation
