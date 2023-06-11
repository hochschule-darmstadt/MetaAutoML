from grpc_omaml import Configuration, DynamicParameterValue
from dataset.dataset_configuration import TrainingConfiguration
from config.config_accessor import get_training_runtime_limit


def training_configuration_to_omaml_config(
    training_config: TrainingConfiguration,
) -> Configuration:
    parameters = {
        parName: DynamicParameterValue(valuesHolder.values)
        for parName, valuesHolder in training_config.parameters.items()
    }
    parameters[":metric"] = DynamicParameterValue([training_config.metric])

    return Configuration(
        training_config.task,
        training_config.target,
        training_config.enabled_strategies,
        training_config.runtime_limit or get_training_runtime_limit(),
        training_config.metric,
        [],
        [],
        parameters,
    )
