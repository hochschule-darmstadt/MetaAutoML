from collections import OrderedDict
from typing import Any, Dict, List
from jsonschema import validate
from os import path
from typing import cast
import yaml

from dataset.dataset_configuration import (
    DatasetColumnConfiguration,
    DatasetConfigurationHolder,
    DatasetConfiguration,
)

from config.constants import resource_directory


def read_dataset_configuration() -> List[DatasetConfiguration]:
    schema: Any
    datasetHolderDict: Dict[Any, Any]
    schemaPath = path.join(resource_directory, "schema.yaml")
    datasetsPath = path.join(resource_directory, "datasets.yaml")
    with open(schemaPath, "r") as schemafile:
        schema = yaml.safe_load(schemafile)
    with open(datasetsPath, "r") as file:
        datasetHolderDict = yaml.safe_load(file)
    validate(datasetHolderDict, schema)
    return __dict_to_dataset_configuration_holder(datasetHolderDict).datasets


__dict_type = Dict[str, str | int | List[Dict[Any, Any]]]


def __dict_to_dataset_configuration_holder(
    datasetHolderDict: __dict_type,
) -> DatasetConfigurationHolder:
    return cast(
        DatasetConfigurationHolder,
        __create_namedtuple_from_dict(datasetHolderDict, DatasetConfigurationHolder),
    )


__named_tuple_type = (
    DatasetConfigurationHolder | DatasetConfiguration | DatasetColumnConfiguration
)


def __create_namedtuple_from_dict(
    obj: Any, tupleType: type | None
) -> __named_tuple_type | List[__named_tuple_type]:
    if isinstance(obj, dict):
        if tupleType is None:
            raise ValueError("tupleType must not be None if obj is a dict")
        nextType: type | None
        if tupleType == DatasetConfigurationHolder:
            nextType = DatasetConfiguration
        elif tupleType == DatasetConfiguration:
            nextType = DatasetColumnConfiguration
        else:
            nextType = None
        castedObj = cast(__dict_type, obj)
        fields = sorted(castedObj.keys())
        field_value_pairs = OrderedDict(
            (
                str(field),
                cast(
                    str | int | __named_tuple_type,
                    __create_namedtuple_from_dict(castedObj[field], nextType),
                ),
            )
            for field in fields
        )
        return tupleType(**field_value_pairs)
    elif isinstance(obj, (list, set, tuple, frozenset)):
        if tupleType is None:
            raise ValueError(
                "nextType must not be None if obj is a list (assuming, that there are only lists of objects and never lists of primitive types)"
            )
        return cast(
            List[__named_tuple_type],
            [
                __create_namedtuple_from_dict(item, tupleType)
                for item in cast(List[__dict_type], obj)
            ],
        )
    else:
        return obj
