"""Type definitions for dataset related things.
"""

from typing import List


class DatasetColumnConfiguration:
    index: int
    column_role: str
    column_type: str


class DatasetConfiguration:
    name_id: str
    dataset_type: str
    file_location: str
    columns: List[DatasetColumnConfiguration] = []
