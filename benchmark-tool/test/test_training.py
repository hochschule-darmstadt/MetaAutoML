from unittest.mock import MagicMock
import pytest
from mocking_helpers.mocking_helper import async_lambda, MockingHelper, dummy_uuid
import asyncio

pytest_plugins = ["pytest_asyncio"]

__mocking_helper = MockingHelper()


# reset all mocks after each test
@pytest.fixture(autouse=True)
def setup_function():
    __mocking_helper.add_main_module("training.training")
    yield
    __mocking_helper.reset_mocks()


@pytest.mark.asyncio
async def test_wait_for_training_should_only_return_as_soon_as_training_completed():
    from training.training import wait_for_training

    __mocking_helper.mock_import(
        "external.sleeper", MagicMock(sleep=async_lambda(lambda _: asyncio.sleep(0.1)))
    )

    training_completed = False

    mocked_client = MagicMock(
        get_training_completed=async_lambda(lambda _, __: training_completed)
    )

    wait_for_training_task = asyncio.create_task(
        wait_for_training(mocked_client, dummy_uuid, "test")
    )

    assert not wait_for_training_task.done()

    training_completed = True

    await asyncio.sleep(0.2)
    assert wait_for_training_task.done()
