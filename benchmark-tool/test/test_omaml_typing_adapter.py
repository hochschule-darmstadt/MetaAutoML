from unittest.mock import MagicMock
from dataset.dataset_configuration import TrainingConfiguration, TrainingParameter
from mocking_helpers.mocking_helper import MockingHelper
import pytest

__mocker = MockingHelper()


@pytest.fixture(autouse=True)
def setup_function():
    """resets all mocks after each test"""
    __mocker.add_main_module("grpc_omaml.omaml_typing_adapter")
    __setup_training_time_limit_config()
    yield
    __mocker.reset_mocks()


__default_runtime_limit = 123


def __setup_training_time_limit_config():
    __mocker.mock_import(
        "config.config_accessor",
        MagicMock(get_training_runtime_limit=lambda: __default_runtime_limit),
    )


def __create_minimal_training_configuration():
    return TrainingConfiguration("task", "target", "metric", ["automl1", "automl2"])


def test_training_configuration_to_omaml_config_should_return_correct_config_when_only_scalar_values_are_filled():
    from grpc_omaml.omaml_typing_adapter import (
        training_configuration_to_omaml_config,
    )

    training_config = __create_minimal_training_configuration()
    config = training_configuration_to_omaml_config(training_config)

    assert config.metric == training_config.metric
    assert config.task == training_config.task
    assert config.target == training_config.target


def test_training_configuration_to_omaml_config_should_set_time_limit_to_env_when_not_filled_in_training_config():
    from grpc_omaml.omaml_typing_adapter import (
        training_configuration_to_omaml_config,
    )

    config = training_configuration_to_omaml_config(
        __create_minimal_training_configuration()
    )

    assert config.runtime_limit == __default_runtime_limit


def test_training_configuration_to_omaml_config_should_set_time_limit_to_value_from_training_config():
    from grpc_omaml.omaml_typing_adapter import (
        training_configuration_to_omaml_config,
    )

    training_config = __create_minimal_training_configuration()
    training_config.runtime_limit = 456
    config = training_configuration_to_omaml_config(training_config)

    assert config.runtime_limit == 456


def test_training_configuration_to_omaml_config_should_set_parameters_to_dict_containing_only_metric_when_parameters_are_not_filled():
    from grpc_omaml.omaml_typing_adapter import (
        training_configuration_to_omaml_config,
    )

    config = training_configuration_to_omaml_config(
        __create_minimal_training_configuration()
    )

    assert config.parameters.__len__() == 1
    assert ":metric" in config.parameters


def test_training_configuration_to_omaml_config_should_convert_parameters_when_parameters_are_filled():
    from grpc_omaml.omaml_typing_adapter import (
        training_configuration_to_omaml_config,
    )

    training_config = __create_minimal_training_configuration()
    training_config.parameters = {
        "param1": TrainingParameter(["val1"]),
        "param2": TrainingParameter(["val2", "val3"]),
    }
    config = training_configuration_to_omaml_config(training_config)

    assert config.parameters.__len__() == 3
    assert config.parameters["param1"].values == ["val1"]
    assert config.parameters["param2"].values == ["val2", "val3"]


def test_training_configuration_to_omaml_config_should_add_metric_to_parameters():
    from grpc_omaml.omaml_typing_adapter import (
        training_configuration_to_omaml_config,
    )

    training_config = __create_minimal_training_configuration()
    training_config.parameters = {
        "param1": TrainingParameter(["val1"]),
        "param2": TrainingParameter(["val2", "val3"]),
    }
    config = training_configuration_to_omaml_config(training_config)

    assert config.parameters.__len__() == 3
    assert config.parameters["param1"].values == ["val1"]
    assert config.parameters["param2"].values == ["val2", "val3"]
    assert config.parameters[":metric"].values == [training_config.metric]


def test_training_configuration_to_omaml_config_should_set_automls():
    from grpc_omaml.omaml_typing_adapter import (
        training_configuration_to_omaml_config,
    )

    training_config = __create_minimal_training_configuration()
    config = training_configuration_to_omaml_config(training_config)

    assert config.selected_auto_ml_solutions == training_config.auto_mls


def test_training_configuration_to_omaml_configuration_should_set_selected_auto_ml_libraries_to_all():
    from grpc_omaml.omaml_typing_adapter import (
        training_configuration_to_omaml_config,
        all_libs,
    )

    training_config = __create_minimal_training_configuration()
    config = training_configuration_to_omaml_config(training_config)

    assert config.selected_ml_libraries == all_libs
