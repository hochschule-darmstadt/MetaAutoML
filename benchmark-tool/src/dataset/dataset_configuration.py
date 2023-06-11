"""Type definitions for dataset related things.
"""

from typing import List
from dataclasses import dataclass, field


@dataclass
class DatasetColumnConfiguration:
    column_name: str
    column_type: str
    column_role: str = ""


@dataclass
class TrainingParameter:
    values: list[str] = field(default_factory=list)


@dataclass
class TrainingConfiguration:
    task: str
    target: str
    metric: str
    auto_mls: List[str]
    enabled_strategies: List[str] = field(default_factory=list)
    runtime_limit: int | None = None
    parameters: dict[str, TrainingParameter] = field(default_factory=dict)


@dataclass
class DatasetConfiguration:
    name_id: str
    dataset_type: str
    file_location: str
    training: TrainingConfiguration
    columns: List[DatasetColumnConfiguration] = field(default_factory=list)


@dataclass
class DatasetConfigurationHolder:
    datasets: List[DatasetConfiguration]
