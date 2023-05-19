from unittest.mock import MagicMock
from uuid import UUID
import pytest
from mocking_helpers.mocking_helper import MockingHelper, async_lambda

pytest_plugins = ["pytest_asyncio"]
__mocker = MockingHelper()


@pytest.fixture(autouse=True)
def setup_function():
    """resets all mocks after each test"""
    __mocker.add_main_module("user.user")
    yield
    __mocker.reset_mocks()


new_user_id = UUID("00000000-0000-0000-0000-000000000001")
config_user_id = "00000000-0000-0000-0000-000000000000"


def call_init_user(client: MagicMock):
    from user.user import init_user

    return init_user(client)


@pytest.mark.asyncio
async def test_init_user_should_create_user_when_user_id_not_set():
    mockedClient = setup_missing_user_id()

    user_id = await call_init_user(mockedClient)
    assert user_id == new_user_id


def setup_missing_user_id():
    __mocker.mock_import(
        "config.config_accessor",
        MagicMock(get_userid=lambda: None),
    )

    return MagicMock(create_user=async_lambda(lambda: new_user_id))


@pytest.mark.asyncio
async def test_init_user_should_use_configured_user_when_user_id_is_set():
    mockedClient = setup_existing_user_id()

    user_id = await call_init_user(mockedClient)
    assert user_id == UUID(config_user_id)


def setup_existing_user_id():
    __mocker.mock_import(
        "config.config_accessor",
        MagicMock(get_userid=lambda: config_user_id),
    )

    return MagicMock(create_user=async_lambda(lambda: new_user_id))
