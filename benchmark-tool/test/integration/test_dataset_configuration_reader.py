"""Tests whether the dataset configuration file is valid and that the configuration reader works.
This is an integration test.
"""

from unittest.mock import MagicMock
from mocking_helpers.mocking_helper import MockingHelper
import pytest


__mocker = MockingHelper()


@pytest.fixture(autouse=True)
def setup_function():
    """resets all mocks after each test"""
    __mocker.add_main_module("dataset.dataset_configuration_reader")
    __mocker.mock_import("config.constants", MagicMock(resource_directory="resources"))
    yield
    __mocker.reset_mocks()


def test_read_dataset_configuration_should_return_valid_configuration():
    from dataset.dataset_configuration_reader import read_dataset_configuration

    result = read_dataset_configuration()
    assert len(result) > 0
    assert result[0].name_id != ""
    assert result[0].dataset_type != ""
    assert result[0].file_location != ""
    assert len(result[0].columns) > 0
