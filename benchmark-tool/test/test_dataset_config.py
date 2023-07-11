from unittest.mock import MagicMock
from dataset.dataset_configuration import (
    DatasetConfiguration,
    DatasetColumnConfiguration,
    TrainingConfiguration,
)
from mocking_helpers.mocking_helper import async_lambda
import pytest


@pytest.mark.asyncio
async def test_configure_dataset_should_call_adapter_for_each_column_when_multiple_columns_exist():
    from dataset.dataset import configure_dataset

    set_schema_mock = MagicMock()
    mocked_adapter = MagicMock(set_dataset_column_schema=async_lambda(set_schema_mock))

    dummy_training_config = TrainingConfiguration("test", "test", "test", [])
    dataset_config = DatasetConfiguration(
        "test",
        ":tabular",
        "test",
        dummy_training_config,
        [
            DatasetColumnConfiguration("abc", ":integer"),
            DatasetColumnConfiguration("def", ":integer"),
        ],
    )

    await configure_dataset(mocked_adapter, MagicMock(), "1", dataset_config)

    assert set_schema_mock.call_count == 2
    assert (
        set_schema_mock.call_args_list[0].kwargs["dataset_column"].column_name == "abc"
    )
    assert (
        set_schema_mock.call_args_list[1].kwargs["dataset_column"].column_name == "def"
    )
