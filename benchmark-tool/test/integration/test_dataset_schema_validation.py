"""Tests whether the yaml schema finds the potential errors in the configuration.
This is an integration test.
"""


from typing import Any, Dict
from unittest.mock import MagicMock
from mocking_helpers.mocking_helper import MockingHelper
import pytest
from jsonschema.exceptions import ValidationError


__mocker = MockingHelper()


@pytest.fixture(autouse=True)
def setup_function():
    """resets all mocks after each test"""
    __mocker.add_main_module("external.yaml_schema_validator")
    __mocker.mock_import("config.constants", MagicMock(resource_directory="resources"))
    yield
    __mocker.reset_mocks()


def __create_valid_dataset_config() -> Dict[str, Any]:
    return {
        "datasets": [
            {
                "name_id": "test",
                "dataset_type": ":tabular",
                "file_location": "test",
                "columns": [
                    {
                        "idx": 0,
                        "column_type": ":float",
                        "column_role": ":ignore",
                    }
                ],
            }
        ]
    }


def test_validate_dataset_config_should_raise_error_when_required_prop_is_missing():
    from external.yaml_schema_validator import validate_dataset_config

    with pytest.raises(
        ValidationError, match=".*'dataset_type' is a required property.*"
    ):
        config = __create_valid_dataset_config()
        del config["datasets"][0]["dataset_type"]
        validate_dataset_config(config)


def test_validate_dataset_config_should_raise_error_when_value_of_prop_is_invalid():
    from external.yaml_schema_validator import validate_dataset_config

    with pytest.raises(ValidationError, match=".*'invalid' is not one of.*"):
        config = __create_valid_dataset_config()
        config["datasets"][0]["dataset_type"] = "invalid"
        validate_dataset_config(config)


def test_validate_dataset_config_should_raise_error_when_has_no_datasets():
    from external.yaml_schema_validator import validate_dataset_config

    with pytest.raises(ValidationError, match=".*'datasets' is a required property.*"):
        config = __create_valid_dataset_config()
        del config["datasets"]
        validate_dataset_config(config)
