#lookup dictionary for AutoPytorch metrics values
#https://github.com/automl/Auto-PyTorch/blob/master/autoPyTorch/pipeline/components/training/metrics/metrics.py
autopytorch_metrics = {
    #classification
    ":accuracy": "accuracy",
    ":balanced_accuracy": "balanced_accuracy",
    ":f_measure": "f1",
    ":roc_auc": "roc_auc",
    ":average_precision": "average_precision",
    ":precision": "precision",
    ":recall": "recall",
    ":log_loss": "log_loss",

    #regression
    ":mean_absolute_error": "mean_absolute_error",
    ":mean_squared_error": "mean_squared_error",
    ":rooted_mean_squared_error": "root_mean_squared_error",
    ":mean_squared_log_error ": "mean_squared_log_error",
    ":median_absolute_error ": "median_absolute_error",
    ":r2": "r2"
}

#configs for the different tasks that can be executed with AutoPytorch
#each parameter has its own line that contains:
#the broader type of the parameter(broader id); the autoML specific parameter id; the default value in case no parameter-value is selected;
#the expected amount of the parameters(single_value/list); the type to which it should be converted (integer/dictionary); the lookup dictionary which includes the converting types;
#the autoML function parameter names
#[broader_type, specific_type, default, expected parameter 'count', converting type, lookup dictionary, used name by autoML]

#config for the tabular classification
tabular_classification_config = [
    [":metric", ":metric_autopytorch_tabular_classification", [":accuracy"], "single_value", "dict", autopytorch_metrics, "optimize_metric"]
]

#config for the tabular regression
tabular_regression_config = [
    [":metric", ":metric_autopytorch_tabular_regression", [":r2"], "single_value", "dict", autopytorch_metrics, "optimize_metric"]
]

#config for the tabular regression
time_series_forcasting_config = [
    [":metric", ":metric_autopytorch_time_series_forcasting", [":mean_squared_error"], "single_value", "dict", autopytorch_metrics, "optimize_metric"]
]

# dictionary for mapping the selected task to the appropriate config
task_config = {
    ":tabular_classification": tabular_classification_config,
    ":tabular_regression": tabular_regression_config,
    ":time_series_forecasting": time_series_forcasting_config
}
