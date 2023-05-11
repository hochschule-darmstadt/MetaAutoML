from unittest.mock import MagicMock
from uuid import UUID
import pytest
from mocking_helpers.mocking_helper import MockingHelper, async_lambda

pytest_plugins = ["pytest_asyncio"]
__mocker = MockingHelper()


@pytest.fixture(autouse=True)
def setup_function():
    """resets all mocks after each test"""
    yield
    __mocker.reset_mocks()


new_user_id = UUID("00000000-0000-0000-0000-000000000001")
config_user_id = "00000000-0000-0000-0000-000000000000"


def call_init_user():
    from user.user import init_user

    __mocker.add_main_module("user.user")
    return init_user()


@pytest.mark.asyncio
async def test_init_user_should_create_user_when_user_id_not_set():
    setup_missing_user_id()

    user_id = await call_init_user()
    assert user_id == new_user_id


def setup_missing_user_id():
    __mocker.mock_import(
        "config.config_accessor",
        MagicMock(get_userid=lambda: None),
    )
    __mocker.mock_import(
        "user.omaml_user_adapter",
        MagicMock(create_user=async_lambda(lambda: new_user_id)),
    )


@pytest.mark.asyncio
async def test_init_user_should_use_configured_user_when_user_id_is_set():
    setup_existing_user_id()

    user_id = await call_init_user()
    assert user_id == UUID(config_user_id)


def setup_existing_user_id():
    __mocker.mock_import(
        "config.config_accessor",
        MagicMock(get_userid=lambda: config_user_id),
    )
    __mocker.mock_import(
        "user.omaml_user_adapter",
        MagicMock(create_user=async_lambda(lambda: new_user_id)),
    )
