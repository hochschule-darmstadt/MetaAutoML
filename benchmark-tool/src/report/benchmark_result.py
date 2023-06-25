from dataclasses import dataclass


@dataclass
class BenchmarkResult:
    dataset_name: str
    auto_ml_solution: str
    target_metric: str
    achieved_score: str


@dataclass
class TrainingResult:
    auto_ml_solution: str
    achieved_score: str
    is_failed: bool
