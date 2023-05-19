from unittest.mock import MagicMock
import pytest
from dataset.dataset_type import DatasetType
from mocking_helpers.mocking_helper import async_lambda
from uuid import UUID

pytest_plugins = ["pytest_asyncio"]


@pytest.mark.asyncio
async def test_upload_dataset_should_set_name_to_titanic_and_type_to_tabular():
    from dataset.dataset import upload_dataset

    create_dataset_mock = MagicMock()
    mocked_client = MagicMock(create_dataset=async_lambda(create_dataset_mock))

    await upload_dataset(mocked_client, UUID("00000000-0000-0000-0000-000000000000"))

    passed_args = create_dataset_mock.call_args.kwargs
    assert passed_args["name"] == "titanic"
    assert passed_args["dataset_type"] == DatasetType.TABULAR
