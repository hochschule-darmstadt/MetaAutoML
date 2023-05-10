from enum import Enum


class DatasetType(Enum):
    TABULAR = 1


async def create_dataset(
    name: str, file_location: str, dataset_type: DatasetType
) -> None:
    pass
