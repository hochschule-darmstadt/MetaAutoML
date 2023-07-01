from unittest.mock import MagicMock
import pytest
from dataset.dataset_configuration import DatasetConfiguration, TrainingConfiguration
from mocking_helpers.mocking_helper import async_lambda, MockingHelper, dummy_uuid
import asyncio

pytest_plugins = ["pytest_asyncio"]

__mocking_helper = MockingHelper()


# reset all mocks after each test
@pytest.fixture(autouse=True)
def setup_function():
    __mocking_helper.add_main_module("dataset.dataset")
    __mocking_helper.mock_import(
        "config.config_accessor",
        MagicMock(get_dataset_analysis_timeout_seconds=lambda: 1),
    )
    yield
    __mocking_helper.reset_mocks()


__existing_dataset_id = "1234567890"
__dataset = DatasetConfiguration(
    name_id="titanic",
    dataset_type=":tabular",
    file_location="some/path/to/file.csv",
    training=TrainingConfiguration(
        "test", "test", "test", []
    ),  # training config does not matter for this test
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
        verify_dataset_ready=async_lambda(lambda _, __: True),
    )

    return mocked_client, create_dataset_mock


@pytest.mark.asyncio
async def test_upload_dataset_should_upload_dataset_when_dataset_does_not_exist_yet():
    from dataset.dataset import upload_dataset

    mocked_client, create_dataset_mock = mock_omaml_client(dataset_exists=False)

    await upload_dataset(mocked_client, dummy_uuid, __dataset)

    assert create_dataset_mock.called


@pytest.mark.asyncio
async def test_upload_dataset_should_not_upload_when_dataset_already_exists():
    from dataset.dataset import upload_dataset

    mocked_client, create_dataset_mock = mock_omaml_client(dataset_exists=True)

    await upload_dataset(mocked_client, dummy_uuid, __dataset)

    assert not create_dataset_mock.called


@pytest.mark.asyncio
async def test_upload_dataset_should_return_dataset_guid_when_dataset_already_exists():
    from dataset.dataset import upload_dataset

    mocked_client, _ = mock_omaml_client(dataset_exists=True)

    dataset_id = await upload_dataset(mocked_client, dummy_uuid, __dataset)

    assert dataset_id == __existing_dataset_id


@pytest.mark.asyncio
async def test_upload_dataset_should_return_dataset_guid_when_dataset_does_not_exist_yet():
    from dataset.dataset import upload_dataset

    mocked_client, _ = mock_omaml_client(dataset_exists=False)

    dataset_id = await upload_dataset(mocked_client, dummy_uuid, __dataset)

    assert dataset_id is not None
    assert len(dataset_id) > 0
    assert dataset_id != __existing_dataset_id


@pytest.mark.asyncio
async def test_upload_dataset_should_only_return_as_soon_as_dataset_is_ready():
    from dataset.dataset import upload_dataset

    is_dataset_ready = False

    mocked_client, _ = mock_omaml_client(dataset_exists=False)
    mocked_client.verify_dataset_ready = async_lambda(lambda _, __: is_dataset_ready)

    uploading_task = asyncio.create_task(
        upload_dataset(mocked_client, dummy_uuid, __dataset)
    )

    assert not uploading_task.done()

    is_dataset_ready = True

    await asyncio.sleep(0.2)
    assert uploading_task.done()
