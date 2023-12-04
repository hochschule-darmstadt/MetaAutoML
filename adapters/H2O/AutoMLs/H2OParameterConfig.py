#
# This Class contains the configuration objects for the AutoKerasAdapter
#

import keras_tuner

#max_runtime_secs
#max_models
#stopping_metric
#sort_metric
#include_algos/exclude_algos

h2o_metrics = {
    # TODO: Check if needed and add to :Metric
    #deviance (mean residual deviance) - not in ontology yet or mean_poisson_deviance? 2x(LL(Saturated Model) - LL(Proposed Model))?
    #":auto": "AUTO", not in ontology yet This defaults to logloss for classification and deviance for regression.
    ":log_loss": "logloss",
    ":mean_squared_error": "MSE",
    ":root_mean_squared_error": "RMSE",
    ":mean_absolute_error": "MAE",
    ":root_mean_squared_log_error": "RMSLE",
    ":area_under_roc_curve": "AUC",
    ":area_under_precision_recall_curve" : "AUCPR", #AUCPR  (area under the Precision-Recall curve) - not in ontology yet
    #lift_top_group - not in ontology yet
    #misclassification - probably :mean_absolute_error or :mean_absolute_percentage_error, but not sure whether its absolute or relative
    #mean_per_class_error - not in ontology yet
}

#lookup dictionary for autokeras objectives values
#objectives means which metric is choosen for optimizing the ML model
# -> Gibt es in h2o nicht

#lookup dictionary for autokeras loss classification values
autokeras_loss_classification = {
    ":binary_cross_entropy": "binary_crossentropy",
    ":categorical_cross_entropy": "categorical_crossentropy"
}

#lookup dictionary for autokeras loss regression values
autokeras_loss_regression = {
    ":mean_squared_error": "mean_squared_error",
}

#lookup dictionary for autokeras tuner values
autokeras_tuner = {
    ":greedy": "greedy",
    ":bayesian":"bayesian",
    ":random": "random",
    ":hyperband": "hyperband"
}

#max_runtime_secs
#max_models
#stopping_metric
#sort_metric
#include_algos/exclude_algos
parameters = {
    #tabular classification
    ":metric_autokeras_tabular_classification": {
                                                    "parameter_name": "objective",
                                                    "lookup_dict": autokeras_objectives
                                                },
    ":loss_function_autokeras_tabular_classification": {
                                                    "parameter_name": "loss",
                                                    "lookup_dict": autokeras_loss_classification
                                                },
    ":max_trials_autokeras_tabular_classification": {
                                                    "parameter_name": "max_trials",
                                                    "default": [1]
                                                },
    ":tuner_autokeras_tabular_classification": {
                                                    "parameter_name": "tuner",
                                                    "lookup_dict": autokeras_tuner
                                                },
    ":max_model_size_autokeras_tabular_classification": {
                                                    "parameter_name": "max_model_size"
                                                },
    # tabular regression
    ":metric_autokeras_tabular_regression": {
                                                    "parameter_name": "objective",
                                                    "lookup_dict": autokeras_objectives
                                                },
    ":loss_function_autokeras_tabular_regression": {
                                                    "parameter_name": "loss",
                                                    "lookup_dict": autokeras_loss_regression
                                                },
    ":max_trials_autokeras_tabular_regression": {
                                                    "parameter_name": "max_trials",
                                                    "default": [1]
                                                },
    ":tuner_autokeras_tabular_regression": {
                                                    "parameter_name": "tuner",
                                                    "lookup_dict": autokeras_tuner
                                                },
    ":max_model_size_autokeras_tabular_regression": {
                                                    "parameter_name": "max_model_size"
                                                },
    #image classification
    ":metric_autokeras_image_classification": {
                                                    "parameter_name": "objective",
                                                    "lookup_dict": autokeras_objectives
                                                },
    ":loss_function_autokeras_image_classification": {
                                                    "parameter_name": "loss",
                                                    "lookup_dict": autokeras_loss_classification
                                                },
    ":max_trials_autokeras_image_classification": {
                                                    "parameter_name": "max_trials",
                                                    "default": [1]
                                                },
    ":tuner_autokeras_image_classification": {
                                                    "parameter_name": "tuner",
                                                    "lookup_dict": autokeras_tuner
                                                },
    ":max_model_size_autokeras_image_classification": {
                                                    "parameter_name": "max_model_size"
                                                },
    #image regression
    ":metric_autokeras_image_regression": {
                                                    "parameter_name": "objective",
                                                    "lookup_dict": autokeras_objectives
                                                },
    ":loss_function_autokeras_image_regression": {
                                                    "parameter_name": "loss",
                                                    "lookup_dict": autokeras_loss_regression
                                                },
    ":max_trials_autokeras_image_regression": {
                                                    "parameter_name": "max_trials",
                                                    "default": [1]
                                                },
    ":tuner_autokeras_image_regression": {
                                                    "parameter_name": "tuner",
                                                    "lookup_dict": autokeras_tuner
                                                },
    ":max_model_size_autokeras_image_regression": {
                                                    "parameter_name": "max_model_size"
                                                },
    #text classification
    ":metric_autokeras_text_classification": {
                                                    "parameter_name": "objective",
                                                    "lookup_dict": autokeras_objectives
                                                },
    ":loss_function_autokeras_text_classification": {
                                                    "parameter_name": "loss",
                                                    "lookup_dict": autokeras_loss_classification
                                                },
    ":max_trials_autokeras_text_classification": {
                                                    "parameter_name": "max_trials",
                                                    "default": [1]
                                                },
    ":tuner_autokeras_text_classification": {
                                                    "parameter_name": "tuner",
                                                    "lookup_dict": autokeras_tuner
                                                },
    ":max_model_size_autokeras_text_classification": {
                                                    "parameter_name": "max_model_size"
                                                },
    #text regression
    ":metric_autokeras_text_regression": {
                                                    "parameter_name": "objective",
                                                    "lookup_dict": autokeras_objectives
                                                },
    ":loss_function_autokeras_text_regression": {
                                                    "parameter_name": "loss",
                                                    "lookup_dict": autokeras_loss_regression
                                                },
    ":max_trials_autokeras_text_regression": {
                                                    "parameter_name": "max_trials",
                                                    "default": [1]
                                                },
    ":tuner_autokeras_text_regression": {
                                                    "parameter_name": "tuner",
                                                    "lookup_dict": autokeras_tuner
                                                },
    ":max_model_size_autokeras_text_regression": {
                                                    "parameter_name": "max_model_size"
                                                },
    # time series forecasting
    ":metric_autokeras_time_series_forecasting": {
                                                    "parameter_name": "objective",
                                                    "lookup_dict": autokeras_objectives
                                                },
    ":loss_function_autokeras_time_series_forecasting": {
                                                    "parameter_name": "loss",
                                                    "lookup_dict": autokeras_loss_classification
                                                },
    ":max_trials_autokeras_time_series_forecasting": {
                                                    "parameter_name": "max_trials",
                                                    "default": [1]
                                                },
    ":tuner_autokeras_time_series_forecasting": {
                                                    "parameter_name": "tuner",
                                                    "lookup_dict": autokeras_tuner
                                                },
    ":max_model_size_autokeras_time_series_forecasting": {
                                                    "parameter_name": "max_model_size"
                                                },
    ":forecasting_horizon_autokeras_time_series_forcasting": {
                                                    "parameter_name": "predict_until",
                                                    "default": [1]
                                                    },
    ":lookback_autokeras_time_series_forcasting": {
                                                    "parameter_name": "lookback",
                                                    },
    ":gap_autokeras_time_series_forcasting": {
                                                    "parameter_name": "predict_from",
                                                    }
}
