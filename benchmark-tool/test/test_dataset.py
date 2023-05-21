from unittest.mock import MagicMock
import pytest
from dataset.dataset_type import DatasetType
from mocking_helpers.mocking_helper import async_lambda
from uuid import UUID

pytest_plugins = ["pytest_asyncio"]


def mock_omaml_client(dataset_exists: bool):
    create_dataset_mock = MagicMock()
    mocked_client = MagicMock(
        create_dataset=async_lambda(create_dataset_mock),
        dataset_exists=async_lambda(lambda _, __: dataset_exists),
    )

    return mocked_client, create_dataset_mock


def assert_titanic_dataset_uploaded(create_dataset_mock: MagicMock):
    assert create_dataset_mock.called
    passed_args = create_dataset_mock.call_args.kwargs
    assert passed_args["name"] == "titanic"
    assert passed_args["dataset_type"] == DatasetType.TABULAR


@pytest.mark.asyncio
async def test_upload_dataset_should_upload_titanic_dataset_when_dataset_does_not_exist_yet():
    from dataset.dataset import upload_dataset

    mocked_client, create_dataset_mock = mock_omaml_client(dataset_exists=False)

    await upload_dataset(mocked_client, UUID("00000000-0000-0000-0000-000000000000"))

    assert_titanic_dataset_uploaded(create_dataset_mock)


@pytest.mark.asyncio
async def test_upload_dataset_should_not_upload_when_dataset_already_exists():
    from dataset.dataset import upload_dataset

    mocked_client, create_dataset_mock = mock_omaml_client(dataset_exists=True)

    await upload_dataset(mocked_client, UUID("00000000-0000-0000-0000-000000000000"))

    assert not create_dataset_mock.called
