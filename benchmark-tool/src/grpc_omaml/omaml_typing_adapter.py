from grpc_omaml import Configuration, DynamicParameterValue
from dataset.dataset_configuration import TrainingConfiguration
from config.config_accessor import get_training_runtime_limit

all_libs = [
    ":catboost_lib",
    ":fastai_lib",
    ":gluonts_lib",
    ":greykite_lib",
    ":h2o_lib",
    ":ibm_snap_ml_lib",
    ":kats_lib",
    ":keras_lib",
    ":lightgbm_lib",
    ":mllib_lib",
    ":mxnet_lib",
    ":pmdarima_lib",
    ":prophet_lib",
    ":pyflux_lib",
    ":pytorch_forecasting_lib",
    ":pytorch_lib",
    ":pywavelets_lib",
    ":scikit_learn_lib",
    ":sktime_lib",
    ":statsmodel_lib",
    ":tensorflow_lib",
    ":tsfresh_lib",
    ":tslearn_lib",
    ":weka_lib",
    ":xgboost_lib",
]


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
        training_config.auto_mls,
        all_libs,
        parameters,
    )
