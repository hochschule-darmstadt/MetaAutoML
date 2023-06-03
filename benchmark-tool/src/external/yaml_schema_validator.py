from os import path
from typing import Any, Dict
from jsonschema import validate

import yaml
from config.constants import resource_directory


def validate_dataset_config(obj: Dict[Any, Any]) -> None:
    schemaPath = path.join(resource_directory, "schema.yaml")
    with open(schemaPath, "r") as schemafile:
        schema = yaml.safe_load(schemafile)
        validate(obj, schema)
