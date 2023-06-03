"""Type definitions for dataset related things.
"""

from typing import List
from dataclasses import dataclass, field


@dataclass
class DatasetColumnConfiguration:
    idx: int
    column_type: str
    column_role: str | None = None


@dataclass
class DatasetConfiguration:
    name_id: str
    dataset_type: str
    file_location: str
    columns: List[DatasetColumnConfiguration] = field(default_factory=list)


@dataclass
class DatasetConfigurationHolder:
    datasets: List[DatasetConfiguration]
