"""Type definitions for dataset related things.
"""

from typing import List, NamedTuple


class DatasetColumnConfiguration(NamedTuple):
    index: int
    column_role: str
    column_type: str


class DatasetConfiguration(NamedTuple):
    name_id: str
    dataset_type: str
    file_location: str
    columns: List[DatasetColumnConfiguration] = []


class DatasetConfigurationHolder(NamedTuple):
    datasets: List[DatasetConfiguration]
