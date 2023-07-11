from unittest.mock import MagicMock
from mocking_helpers.mocking_helper import MockingHelper
import pytest

__mocker = MockingHelper()


@pytest.fixture(autouse=True)
def setup_function():
    """resets all mocks after each test"""
    yield
    __mocker.reset_mocks()


def __call_validate_config_values():
    from config.config_validator import validate_config_values

    __mocker.add_main_module("config.config_validator")
    return validate_config_values()


def __mock_config_accessor(mock: MagicMock):
    __mocker.mock_import("config.config_accessor", mock)


def __raise_value_error():
    """Raises a ValueError (used for mocking)"""
    raise ValueError("msg")


def test_validate_config_values_should_return_exception_message_when_host_not_set():
    __mock_config_accessor(MagicMock(get_omaml_server_host=__raise_value_error))

    result = __call_validate_config_values()

    assert result == "msg"


def test_validate_config_values_should_complain_when_dataset_location_is_no_directory():
    __mock_config_accessor(
        MagicMock(get_omaml_dataset_location=lambda: "not a directory")
    )
    __mocker.mock_import("external.file_system", MagicMock(is_dir=lambda _: False))

    result = __call_validate_config_values()

    assert result == "OMAML_DATASET_LOCATION is not a directory"


def test_validate_config_values_should_return_none_when_location_is_directory():
    __mock_config_accessor(MagicMock(get_omaml_dataset_location=lambda: "a directory"))
    __mocker.mock_import("external.file_system", MagicMock(is_dir=lambda _: True))

    result = __call_validate_config_values()

    assert result is None
