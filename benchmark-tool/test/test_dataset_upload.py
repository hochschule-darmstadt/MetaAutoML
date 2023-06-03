from unittest.mock import MagicMock
import pytest
from dataset.dataset_configuration import DatasetConfiguration
from mocking_helpers.mocking_helper import async_lambda
from uuid import UUID

pytest_plugins = ["pytest_asyncio"]

__existing_dataset_id = "1234567890"
__dataset = DatasetConfiguration(
    name_id="titanic", dataset_type=":tabular", file_location="some/path/to/file.csv"
)


def mock_omaml_client(dataset_exists: bool):
    create_dataset_mock = MagicMock()

    def create_dataset_mock_side_effect():
        if dataset_exists:
            return __existing_dataset_id
        elif create_dataset_mock.called:
            return "some other string"
        else:
            return None

    mocked_client = MagicMock(
        create_dataset=async_lambda(create_dataset_mock),
        get_dataset_by_name=async_lambda(
            lambda _, __: create_dataset_mock_side_effect()
        ),
    )

    return mocked_client, create_dataset_mock


@pytest.mark.asyncio
async def test_upload_dataset_should_upload_dataset_when_dataset_does_not_exist_yet():
    from dataset.dataset import upload_dataset

    mocked_client, create_dataset_mock = mock_omaml_client(dataset_exists=False)

    await upload_dataset(
        mocked_client, UUID("00000000-0000-0000-0000-000000000000"), __dataset
    )

    assert create_dataset_mock.called


@pytest.mark.asyncio
async def test_upload_dataset_should_not_upload_when_dataset_already_exists():
    from dataset.dataset import upload_dataset

    mocked_client, create_dataset_mock = mock_omaml_client(dataset_exists=True)

    await upload_dataset(
        mocked_client, UUID("00000000-0000-0000-0000-000000000000"), __dataset
    )

    assert not create_dataset_mock.called


@pytest.mark.asyncio
async def test_upload_dataset_should_return_dataset_guid_when_dataset_already_exists():
    from dataset.dataset import upload_dataset

    mocked_client, _ = mock_omaml_client(dataset_exists=True)

    dataset_id = await upload_dataset(
        mocked_client, UUID("00000000-0000-0000-0000-000000000000"), __dataset
    )

    assert dataset_id == __existing_dataset_id


@pytest.mark.asyncio
async def test_upload_dataset_should_return_dataset_guid_when_dataset_does_not_exist_yet():
    from dataset.dataset import upload_dataset

    mocked_client, _ = mock_omaml_client(dataset_exists=False)

    dataset_id = await upload_dataset(
        mocked_client, UUID("00000000-0000-0000-0000-000000000000"), __dataset
    )

    assert dataset_id is not None
    assert len(dataset_id) > 0
    assert dataset_id != __existing_dataset_id
