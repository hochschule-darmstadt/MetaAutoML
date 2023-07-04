from typing import cast
from unittest.mock import MagicMock
import pytest
from mocking_helpers.mocking_helper import async_lambda, MockingHelper, dummy_uuid
import asyncio

from report.benchmark_result import BenchmarkResult, TrainingResult

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


@pytest.mark.asyncio
async def test_report_training_score_should_add_benchmark_result():
    from training.training import report_training_score

    # setup mocks
    mocked_client = MagicMock(
        get_training_score=async_lambda(
            lambda _, __: [
                TrainingResult(":flaml", "0.5", False),
                TrainingResult(":autokeras", "0.6", False),
            ]
        )
    )

    add_benchmark_result_mock = MagicMock()
    mocked_report = MagicMock(add_benchmark_result=add_benchmark_result_mock)

    # call function
    await report_training_score(
        mocked_client,
        dummy_uuid,
        "test",
        mocked_report,
        MagicMock(name_id="name", training=MagicMock(metric="metric")),
    )

    # assert
    assert add_benchmark_result_mock.call_count == 2
    passed_result_flaml = cast(
        BenchmarkResult, add_benchmark_result_mock.mock_calls[0].args[0]
    )
    passed_result_autokeras = cast(
        BenchmarkResult, add_benchmark_result_mock.mock_calls[1].args[0]
    )
    assert passed_result_flaml.auto_ml_solution == ":flaml"
    assert passed_result_flaml.target_metric == "metric"
    assert passed_result_flaml.achieved_score == "0.5"
    assert passed_result_autokeras.auto_ml_solution == ":autokeras"
    assert passed_result_autokeras.target_metric == "metric"
    assert passed_result_autokeras.achieved_score == "0.6"


@pytest.mark.asyncio
async def test_report_training_score_should_set_achieved_score_to_failed_when_solution_failed():
    from training.training import report_training_score

    mocked_client = MagicMock(
        get_training_score=async_lambda(
            lambda _, __: [
                TrainingResult(":flaml", "0.5", False),
                TrainingResult(":autokeras", "", True),
            ]
        )
    )

    add_benchmark_result_mock = MagicMock()
    mocked_report = MagicMock(add_benchmark_result=add_benchmark_result_mock)

    await report_training_score(
        mocked_client,
        dummy_uuid,
        "test",
        mocked_report,
        MagicMock(name_id="name", training=MagicMock(metric="metric")),
    )

    assert add_benchmark_result_mock.call_count == 2
    passed_result_autokeras = cast(
        BenchmarkResult, add_benchmark_result_mock.mock_calls[1].args[0]
    )
    assert passed_result_autokeras.auto_ml_solution == ":autokeras"
    assert passed_result_autokeras.target_metric == "metric"
    assert passed_result_autokeras.achieved_score == "failed"
