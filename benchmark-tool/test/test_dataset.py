from unittest.mock import MagicMock
import pytest
from dataset.dataset_type import DatasetType
from mocking_helpers.mocking_helper import MockingHelper, async_lambda

pytest_plugins = ["pytest_asyncio"]
__mocker = MockingHelper()


@pytest.fixture(autouse=True)
def setup_function():
    """resets all mocks after each test"""
    yield
    __mocker.reset_mocks()


@pytest.mark.asyncio
async def test_upload_dataset_should_set_name_to_titanic_and_type_to_tabular():
    create_dataset_mock = MagicMock()
    module_mock = MagicMock(create_dataset=async_lambda(create_dataset_mock))
    __mocker.mock_import("dataset.omaml_dataset_adapter", module_mock)

    await call_upload_dataset()

    passed_args = create_dataset_mock.call_args.kwargs
    assert passed_args["name"] == "titanic"
    assert passed_args["dataset_type"] == DatasetType.TABULAR


async def call_upload_dataset():
    from dataset.dataset import upload_dataset

    __mocker.add_main_module("dataset.dataset")
    await upload_dataset()
