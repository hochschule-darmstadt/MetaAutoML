from collections import OrderedDict
from typing import Any, Dict, List
from os import path
from typing import cast
import yaml

from dataset.dataset_configuration import (
    DatasetColumnConfiguration,
    DatasetConfigurationHolder,
    DatasetConfiguration,
    TrainingConfiguration,
    TrainingParameter,
)

from config.constants import resource_directory
from external.yaml_schema_validator import validate_dataset_config

__dict_type = Dict[str, str | int | List[Dict[str, Any]]]


def read_dataset_configuration() -> List[DatasetConfiguration]:
    """Reads the dataset configurations from the yaml file.

    Returns:
        List[DatasetConfiguration]: The dataset configurations.
    """
    datasetsPath = path.join(resource_directory, "datasets.yaml")
    with open(datasetsPath, "r") as file:
        datasetHolderDict: __dict_type = yaml.safe_load(file)
        validate_dataset_config(datasetHolderDict)
        return __dict_to_dataset_configuration_holder(datasetHolderDict).datasets


def __dict_to_dataset_configuration_holder(
    datasetHolderDict: __dict_type,
) -> DatasetConfigurationHolder:
    return cast(
        DatasetConfigurationHolder,
        __create_data_object_from_dict(datasetHolderDict, [DatasetConfigurationHolder]),
    )


__dataset_configuration_type = (
    DatasetConfigurationHolder | DatasetConfiguration | DatasetColumnConfiguration
)


def __create_data_object_from_dict(
    obj: Any, targetTypes: List[type] | None
) -> __dataset_configuration_type | List[__dataset_configuration_type]:
    if isinstance(obj, dict):
        if targetTypes is None:
            raise ValueError("targetType must not be None if obj is a dict")
        castedObj = cast(__dict_type, obj)
        fields = sorted(castedObj.keys())
        field_value_pairs = OrderedDict(
            (
                str(field),
                cast(
                    str | int | __dataset_configuration_type,
                    __create_data_object_from_dict(
                        castedObj[field], __get_next_type(targetTypes)
                    ),
                ),
            )
            for field in fields
        )
        for targetType in targetTypes:
            try:
                return targetType(**field_value_pairs)
            except TypeError:
                pass
        raise TypeError("No matching type found for dict")
    elif isinstance(obj, list):
        if targetTypes is None:
            raise ValueError(
                "targetType must not be None if obj is a list (assuming, that there are only lists of objects and never lists of primitive types)"
            )
        return cast(
            List[__dataset_configuration_type],
            [
                __create_data_object_from_dict(item, targetTypes)
                for item in cast(List[__dict_type], obj)
            ],
        )
    else:
        return obj


def __get_next_type(targetType: List[type]) -> List[type] | None:
    types: List[type] = []
    if DatasetConfigurationHolder in targetType:
        types.append(DatasetConfiguration)
    elif DatasetConfiguration in targetType:
        types.append(DatasetColumnConfiguration)
        types.append(TrainingConfiguration)
    elif TrainingConfiguration in targetType:
        types.append(TrainingParameter)
    return types if len(types) > 0 else None
