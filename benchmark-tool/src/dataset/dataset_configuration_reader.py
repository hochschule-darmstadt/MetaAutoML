from typing import Any, List
from jsonschema import validate
from os import path
import yaml

from dataset.dataset_configuration import (
    DatasetConfigurationHolder,
    DatasetConfiguration,
)

from config.constants import resource_directory


def read_dataset_configuration() -> List[DatasetConfiguration]:
    schema: Any
    datasetHolder: DatasetConfigurationHolder
    schemaPath = path.join(resource_directory, "schema.yaml")
    datasetsPath = path.join(resource_directory, "datasets.yaml")
    with open(schemaPath, "r") as schemafile:
        schema = yaml.safe_load(schemafile)
    with open(datasetsPath, "r") as file:
        datasetHolder = yaml.safe_load(file)
    validate(datasetHolder, schema)
    return datasetHolder.datasets
