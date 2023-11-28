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
    #deviance (mean residual deviance) - not in ontology yet or mean_poisson_deviance? 2x(LL(Saturated Model) - LL(Proposed Model))?
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
#when there is no default value for name, a new keras_tuner.Objective is created
#https://keras.io/api/metrics
autokeras_objectives = {
    #accuracy metrics
    ":accuracy": "accuracy",
    ":binary_accuracy": "binary_accuracy",
    ":categorical_accuracy": "categorical_accuracy",
    ":sparse_categorical_accuracy": "sparse_categorical_accuracy",
    ":top_k_categorical_accuracy": "top_k_categorical_accuracy",
    ":sparse_top_k_categorical_accuracy": "sparse_top_k_categorical_accuracy",
    #probabilistic metrics
    ":binary_cross_entropy": "binary_crossentropy" ,
    ":categorical_cross_entropy": "categorical_crossentropy",
    #":sparse_categorical_cross_entropy": "sparse_categorical_crossentropy",    || error: Node: 'SparseSoftmaxCrossEntropyWithLogits/SparseSoftmaxCrossEntropyWithLogits' Received a label value of 1 which is outside the valid range of [0, 1)
    #":kullback_leibler_divergence": "kullback_leibler_divergence",        || ValueError: Unable to restore custom object of type _tf_keras_metric. Please make sure that any custom layers are included in the `custom_objects` arg when calling `load_model()` and make sure that all layers implement `get_config` and `from_config`
    ":poisson": "poisson",
    #regression metrics
    ":mean_squared_error": "mean_squared_error",
    ":root_mean_squared_error": keras_tuner.Objective("val_root_mean_squared_error", direction="min"),
    ":mean_absolute_error": "mean_absolute_error",
    ":mean_absolute_percentage_error": "mean_absolute_percentage_error",
    ":mean_squared_log_error": "mean_squared_logarithmic_error",
    ":cosine_similarity": "cosine_similarity",
    ":log_cosh_error": "logcosh",
    #classification metrics based on true/false positives & negatives
    ":area_under_roc_curve": keras_tuner.Objective("val_auc", direction="max"),
    ":precision": keras_tuner.Objective("val_precision", direction="max"),
    ":recall": keras_tuner.Objective("val_recall", direction="max"),
    ":true_positives": keras_tuner.Objective("val_true_positives", direction="max"),
    ":true_negatives": keras_tuner.Objective("val_true_negatives", direction="max"),
    ":false_positives": keras_tuner.Objective("val_false_positives", direction="min"),
    ":false_negatives": keras_tuner.Objective("val_false_negatives", direction="min"),
    #":precision_at_recall": keras_tuner.Objective("precision_at_recall", direction="max"),     | TypeError: __init__() missing 1 required positional argument: 'recall'
    #":sensitivity_at_specificity": keras_tuner.Objective("sensitivity_at_specificity", direction="max"),        | TypeError: __init__() missing 1 required positional argument: 'specificity'
    #":sepecificity_at_sensitivity": keras_tuner.Objective("sepecificity_at_sensitivity", direction="max"),    | TypeError: __init__() missing 1 required positional argument: 'sensitivity'
    #image segmentation metrics
    ":mean_iou": keras_tuner.Objective("mean_iou", direction="min"),
    #hinge metrics for "maximum-margin" classification
    ":hinge": "hinge",
    ":squared_hinge": "squared_hinge",
    ":categorical_hinge": "categorical_hinge"

    #old metric
    #":binary_intersection_over_union": "binary_intersection_over_union",   not in the keras metrics, for reference: https://keras.io/api/metrics/
}

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
