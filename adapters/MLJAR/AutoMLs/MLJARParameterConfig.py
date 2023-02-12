#lookup dictionary for mljar metrics values
#https://supervised.mljar.com/api/  !!Warning!! Looks like the documentation is outdated
#https://github.com/mljar/mljar-supervised/blob/master/supervised/utils/additional_metrics.py
mljar_metrics = {
    ":log_loss": "logloss",
    ":area_under_roc_curve": "auc",
    ":f_measure": "f1",
    ":accuracy": "accuracy",
    ":precision": "precision",
    ":recall": "recall",
    ":matthews_correlation_coefficient": "mcc",

    #regression
    ":rooted_mean_squared_error": "RMSE",
    ":mean_absolute_error": "MAE",
    ":mean_squared_error": "MSE",
    ":r2": "R2",
    ":mean_absolute_percentage_error": "MAPE"
}

#configs for the different tasks that can be executed with autokeras
#each parameter has its own line that contains:
#the broader type of the parameter(broader id); the autoML specific parameter id; the default value in case no parameter-value is selected;
#the expected amount of the parameters(single_value/list); the type to which it should be converted (integer/dictionary); the lookup dictionary which includes the converting types;
#the autoML function parameter names
#[broader_type, specific_type, default, expected parameter 'count', converting type, lookup dictionary, used name by autoML]

#config for the tabular classification
tabular_classification_config = [
    [":metric", ":metric_mljar_tabular_classification", [":log_loss"], "single_value", "dict", mljar_metrics, "eval_metric"]
]

#config for the tabular regression
tabular_regression_config = [
    [":metric", ":metric_mljar_tabular_regression", [":rooted_mean_squared_error"], "single_value", "dict", mljar_metrics, "eval_metric"]
]

# dictionary for mapping the selected task to the appropriate config
task_config = {
    ":tabular_classification": tabular_classification_config,
    ":tabular_regression": tabular_regression_config
}
