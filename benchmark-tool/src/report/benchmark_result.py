from dataclasses import dataclass


@dataclass
class BenchmarkResult:
    """Holds the result of a training for one dataset and one auto ml solution"""

    dataset_name: str
    auto_ml_solution: str
    target_metric: str
    achieved_score: str


@dataclass
class TrainingResult:
    """Holds the result of a training for one auto ml solution"""

    auto_ml_solution: str
    achieved_score: str
    is_failed: bool
