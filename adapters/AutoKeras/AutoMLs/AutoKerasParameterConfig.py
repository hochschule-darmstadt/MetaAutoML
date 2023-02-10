#
# This Class contains the configuration objects for the AutoKerasAdapter
#

import keras_tuner

#lookup dictionary for autokeras metrics values
#https://keras.io/api/metrics
autokeras_metrics = {
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
    #":sparse_categorical_cross_entropy": "sparse_categorical_crossentropy",
    #":kullback_leibler_divergence": "kullback_leibler_divergence",
    ":poisson": "poisson",
    #regression metrics
    ":mean_squared_error": "mean_squared_error",
    ":root_mean_squared_error": "RootMeanSquaredError",
    ":mean_absolute_error": "mean_absolute_error",
    ":mean_absolut_percentage_error": "mean_absolute_percentage_error",
    ":mean_squared_log_error": "mean_squared_logarithmic_error",
    ":cosine_similarity": "cosine_similarity",
    ":log_cosh_error": "logcosh",
    #classification metrics based on true/false positives & negatives
    ":area_under_roc_curve": "AUC",
    ":precision": "Precision",
    ":recall": "Recall",
    ":true_positives": "TruePositives",
    ":true_negatives": "TrueNegatives",
    ":false_positives": "FalsePositives",
    ":false_negatives": "FalseNegatives",
    #":precision_at_recall": "PrecisionAtRecall",
    #":sensitivity_at_specificity": "SensitivityAtSpecificity",
    #":sepecificity_at_sensitivity": "SpecificityAtSensitivity",
    #image segmentation metrics
    ":mean_iou": "MeanIoU",
    #hinge metrics for "maximum-margin" classification
    ":hinge": "hinge",
    ":squared_hinge": "squared_hinge",
    ":categorical_hinge": "categorical_hinge"

    #old metric
    #":binary_intersection_over_union": "binary_intersection_over_union",   not in the keras metrics, for reference: https://keras.io/api/metrics/
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
    ":mean_absolut_percentage_error": "mean_absolute_percentage_error",
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

#configs for the different tasks that can be executed with autokeras
#each parameter has its own line that contains:
#the broader type of the parameter(broader id); the autoML specific parameter id; the default value in case no parameter-value is selected;
#the expected amount of the parameters(single_value/list); the type to which it should be converted (integer/dictionary); the lookup dictionary which includes the converting types;
#the autoML function parameter names
#[broader_type, specific_type, default, expected parameter 'count', converting type, lookup dictionary, used name by autoML]

#config for the tabular classification
tabular_classification_config = [
    [":max_trials", ":max_trials_autokeras", [3], "single_value", "integer", "", "max_trials"],
    [":metric", ":metric_autokeras_classification", [":accuracy"], "single_value", "dict", autokeras_metrics, "metrics"],
    [":metric", ":metric_autokeras_classification", [":accuracy"], "single_value", "dict", autokeras_objectives, "objective"],
    [":tuner", ":tuner_autokeras", [None], "single_value", "dict", autokeras_tuner, "tuner"],
    [":loss", ":loss_autokeras_classification", [":binary_cross_entropy"], "single_value", "dict", autokeras_loss_classification, "loss"],
    [":max_model_size_autokeras", ":max_model_size_autokeras", [None], "single_value", "integer", "", "max_model_size"]
]

#config for the tabular regression
tabular_regression_config = [
    [":max_trials", ":max_trials_autokeras", [3], "single_value", "integer", "", "max_trials"],
    [":metric", ":metric_autokeras_regression", [":accuracy"], "single_value", "dict", autokeras_metrics, "metrics"],
    [":metric", ":metric_autokeras_regression", [":accuracy"], "single_value", "dict", autokeras_objectives, "objective"],
    [":tuner", ":tuner_autokeras", [None], "single_value", "dict", autokeras_tuner, "tuner"],
    [":loss", ":loss_autokeras_regression", [":mean_squared_error"], "single_value", "dict", autokeras_loss_regression, "loss"],
    [":max_model_size_autokeras", ":max_model_size_autokeras", [None], "single_value", "integer", "", "max_model_size"]
]

#config for the image classification
image_classification_config = [
    [":max_trials", ":max_trials_autokeras", [3], "single_value", "integer", "", "max_trials"],
    [":metric", ":metric_autokeras_image_classification", [":accuracy"], "single_value", "dict", autokeras_metrics, "metrics"],
    [":metric", ":metric_autokeras_image_classification", [":accuracy"], "single_value", "dict", autokeras_objectives, "objective"],
    [":tuner", ":tuner_autokeras", [None], "single_value", "dict", autokeras_tuner, "tuner"],
    [":loss", ":loss_autokeras_classification", [":binary_cross_entropy"], "single_value", "dict", autokeras_loss_classification, "loss"],
    [":max_model_size_autokeras", ":max_model_size_autokeras", [None], "single_value", "integer", "", "max_model_size"]
]

#config for the image regression
image_regression_config = [
    [":max_trials", ":max_trials_autokeras", [3], "single_value", "integer", "", "max_trials"],
    [":metric", ":", [":accuracy"], "single_value", "dict", autokeras_metrics, "metrics"],  #missing metric in ontology
    [":metric", ":", [":accuracy"], "single_value", "dict", autokeras_objectives, "objective"],  #missing metric in ontology
    [":tuner", ":tuner_autokeras", [None], "single_value", "dict", autokeras_tuner, "tuner"],
    [":loss", ":loss_autokeras_regression", [":mean_squared_error"], "single_value", "dict", autokeras_loss_regression, "loss"],
    [":max_model_size_autokeras", ":max_model_size_autokeras", [None], "single_value", "integer", "", "max_model_size"]
]

#config for the text classification
text_classification_config = [
    [":max_trials", ":max_trials_autokeras", [3], "single_value", "integer", "", "max_trials"],
    [":metric", ":metric_autokeras_text_classification", [":accuracy"], "single_value", "dict", autokeras_metrics, "metrics"],
    [":metric", ":metric_autokeras_text_classification", [":accuracy"], "single_value", "dict", autokeras_objectives, "objective"],
    [":tuner", ":tuner_autokeras", [None], "single_value", "dict", autokeras_tuner, "tuner"],
    [":loss", ":loss_autokeras_classification", [":binary_cross_entropy"], "single_value", "dict", autokeras_loss_classification, "loss"],
    [":max_model_size_autokeras", ":max_model_size_autokeras", [None], "single_value", "integer", "", "max_model_size"]
]

#config for the text regression
text_regression_config = [
    [":max_trials", ":max_trials_autokeras", [3], "single_value", "integer", "", "max_trials"],
    [":metric", ":", [":accuracy"], "single_value", "dict", autokeras_metrics, "metrics"], #missing metric in ontology
    [":metric", ":", [":accuracy"], "single_value", "dict", autokeras_objectives, "objective"], #missing metric in ontology
    [":tuner", ":tuner_autokeras", [None], "single_value", "dict", autokeras_tuner, "tuner"],
    [":loss", ":loss_autokeras_regression", [":mean_squared_error"], "single_value", "dict", autokeras_loss_regression, "loss"],
    [":max_model_size_autokeras", ":max_model_size_autokeras", [None], "single_value", "integer", "", "max_model_size"]
]

# config for time series forcasting
time_series_forecasting_config = [
    [":max_trials", ":max_trials_autokeras", [3], "single_value", "integer", "", "max_trials"],
    [":metric", ":", [":accuracy"], "single_value", "dict", autokeras_metrics, "metrics"], #missing metric in ontology
    [":metric", ":", [":accuracy"], "single_value", "dict", autokeras_objectives, "objective"], #missing metric in ontology
    [":tuner", ":tuner_autokeras", [None], "single_value", "dict", autokeras_tuner, "tuner"],
    [":loss", ":", [None], "single_value", "dict", autokeras_loss_regression, "loss"], #missing loss in ontology
    [":max_model_size_autokeras", ":max_model_size_autokeras", [None], "single_value", "integer", "", "max_model_size"]
]

# dictionary for mapping the selected task to the appropriate config
task_config = {
    ":tabular_classification": tabular_classification_config,
    ":tabular_regression": tabular_regression_config,
    ":image_classification": image_classification_config,
    ":image_regression": image_regression_config,
    ":text_classification": text_classification_config,
    ":text_regression": text_regression_config,
    ":time_series_forecasting": time_series_forecasting_config
}
