class ConflictResolutionStrategy:
    STRATEGIES = {
        "student_note": "LAST_WRITE_WINS",
        "attendance": "LAST_WRITE_WINS",
        "conduct_incident": "LAST_WRITE_WINS",
        "project_note": "LAST_WRITE_WINS",
        "early_alert": "SERVER_WINS",
        "evaluative_activity": "SERVER_WINS",
        "enrollment": "MANUAL",
        "recovery_process": "SERVER_WINS",
        "behavior_evaluation": "LAST_WRITE_WINS",
        "skill_evaluation": "LAST_WRITE_WINS",
        "diagnostic_evaluation": "LAST_WRITE_WINS",
        "learning_report": "SERVER_WINS",
    }

    @classmethod
    def resolve(cls, source_table, local_record, remote_payload):
        strategy = cls.STRATEGIES.get(source_table, "LAST_WRITE_WINS")

        if strategy == "LAST_WRITE_WINS":
            return cls._last_write_wins(local_record, remote_payload)
        elif strategy == "SERVER_WINS":
            return cls._server_wins(local_record, remote_payload)
        elif strategy == "MANUAL":
            return cls._manual_resolution_required(local_record, remote_payload)
        return "ACCEPT_REMOTE"

    @classmethod
    def _last_write_wins(cls, local, remote):
        remote_version = remote.get("sync_version", 0)
        if remote_version > local.sync_version:
            return "ACCEPT_REMOTE"
        elif remote_version < local.sync_version:
            return "KEEP_LOCAL"
        return "ACCEPT_REMOTE"

    @classmethod
    def _server_wins(cls, local, remote):
        return "KEEP_LOCAL"

    @classmethod
    def _manual_resolution_required(cls, local, remote):
        local.mark_conflict()
        local.save()
        return "MANUAL"
