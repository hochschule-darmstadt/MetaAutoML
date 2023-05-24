from enum import Enum


class DatasetType(Enum):
    TABULAR = 1


def type_to_omaml_id(type: DatasetType) -> str:
    if type == DatasetType.TABULAR:
        return ":tabular"
    else:
        raise ValueError("Unknown dataset type")
