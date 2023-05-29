from enum import Enum


class DatasetType(Enum):
    TABULAR = 1


def type_to_omaml_id(type: DatasetType) -> str:
    """Gets the ontology id for the given dataset type

    Args:
        type (DatasetType): The given dataset type

    Raises:
        ValueError: When the dataset type is unknown

    Returns:
        str: The ontology id for the given dataset type
    """
    if type == DatasetType.TABULAR:
        return ":tabular"
    else:
        raise ValueError("Unknown dataset type")
