from dataclasses import dataclass


@dataclass(frozen=True)
class RiskTrainingParams:
    n_estimators: int = 200
    max_depth: int = 12
    min_samples_leaf: int = 5
    class_weight: str | None = "balanced"
    cv_splits: int = 5
    random_state: int = 42
    n_jobs: int = -1


def build_training_params(**overrides) -> RiskTrainingParams:
    values = {
        field: getattr(RiskTrainingParams(), field)
        for field in RiskTrainingParams.__dataclass_fields__
    }
    values.update({key: value for key, value in overrides.items() if value is not None})
    if values["class_weight"] == "none":
        values["class_weight"] = None
    return RiskTrainingParams(**values)
