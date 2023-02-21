#lookup dictionary for EvalML metrics values
#https://evalml.alteryx.com/en/stable/autoapi/evalml/objectives/index.html
#https://github.com/alteryx/evalml/blob/main/evalml/objectives/standard_metrics.py
eval_metrics = {
    #classification
    ":accuracy": "Accuracy Multiclass",
    ":balanced_accuracy": "Balanced Accuracy Multiclass",
    ":f_measure": "F1",
    ":f_measure_micro": "F1 Micro",
    ":f_measure_macro": "F1 Macro",
    ":f_measure_weighted": "F1 Weighted",
    ":precision": "Precision",
    ":precision_macro": "Precision Macro",
    ":precision_micro": "Precision Micro",
    ":precision_weighted": "Precision Weighted",
    ":recall": "Recall",
    ":recall_micro": "Recall Micro",
    ":recall_macro": "Recall Macro",
    ":recall_weighted": "Recall Weighted",
    ":area_under_roc_curve": "AUC",
    ":area_under_roc_curve_micro": "AUC Micro",
    ":area_under_roc_curve_macro": "AUC Macro",
    ":area_under_roc_curve_weighted": "AUC Weighted",
    ":gini": "Gini",
    ":log_loss": "Log Loss Multiclass",
    ":matthews_correlation_coefficient": "MCC Multiclass",

    #regression
    ":rooted_mean_squared_error": "Root Mean Squared Error",
    ":rooted_mean_squared_log_error": "Root Mean Squared Log Error",
    ":mean_squared_log_error": "Mean Squared Log Error",
    ":r2": "R2",
    ":mean_absolute_error": "MAE",
    ":mean_squared_error": "MSE",
    ":median_absolute_error": "MedianAE",
    ":max_error": "MaxError",
    ":explained_variance": "ExpVariance",

    #ranking
    ":mean_absolute_percentage_error": "Mean Absolute Percentage Error"
}

eval_metrics_binary = {
    #classification
    ":accuracy": "Accuracy Binary",
    ":balanced_accuracy": "Balanced Accuracy Binary",
    ":f_measure": "F1",
    ":f_measure_micro": "F1 Micro",
    ":f_measure_macro": "F1 Macro",
    ":f_measure_weighted": "F1 Weighted",
    ":precision": "Precision",
    ":precision_macro": "Precision Macro",
    ":precision_micro": "Precision Micro",
    ":precision_weighted": "Precision Weighted",
    ":recall": "Recall",
    ":recall_micro": "Recall Micro",
    ":recall_macro": "Recall Macro",
    ":recall_weighted": "Recall Weighted",
    ":area_under_roc_curve": "AUC",
    ":area_under_roc_curve_micro": "AUC Micro",
    ":area_under_roc_curve_macro": "AUC Macro",
    ":area_under_roc_curve_weighted": "AUC Weighted",
    ":gini": "Gini",
    ":log_loss": "Log Loss Binary",
    ":matthews_correlation_coefficient": "MCC Binary",

    #regression
    ":rooted_mean_squared_error": "Root Mean Squared Error",
    ":rooted_mean_squared_log_error": "Root Mean Squared Log Error",
    ":mean_squared_log_error": "Mean Squared Log Error",
    ":r2": "R2",
    ":mean_absolute_error": "MAE",
    ":mean_squared_error": "MSE",
    ":median_absolute_error": "MedianAE",
    ":max_error": "MaxError",
    ":explained_variance": "ExpVariance",

    #ranking
    ":mean_absolute_percentage_error": "Mean Absolute Percentage Error"
}

#configs for the different tasks that can be executed with EvalML
#each parameter has its own line that contains:
#the broader type of the parameter(broader id); the autoML specific parameter id; the default value in case no parameter-value is selected;
#the expected amount of the parameters(single_value/list); the type to which it should be converted (integer/dictionary); the lookup dictionary which includes the converting types;
#the autoML function parameter names
#[broader_type, specific_type, default, expected parameter 'count', converting type, lookup dictionary, used name by autoML]

#config for the tabular classification
tabular_classification_config = [
    [":metric", ":metric_evalml_tabular_classification", [":log_loss"], "single_value", "dict", eval_metrics, "objective"]
]
tabular_classification_config_binary_metrics = [
    [":metric", ":metric_evalml_tabular_classification", [":log_loss"], "single_value", "dict", eval_metrics_binary, "objective"]
]

#config for the tabular regression
tabular_regression_config = [
    [":metric", ":metric_evalml_tabular_regression", [":r2"], "single_value", "dict", eval_metrics, "objective"]
]

#config for the text classification
text_classification_config = [
    [":metric", ":metric_evalml_text_classification", [":log_loss"], "single_value", "dict", eval_metrics, "objective"]
]
text_classification_config_binary_metrics = [
    [":metric", ":metric_evalml_text_classification", [":log_loss"], "single_value", "dict", eval_metrics_binary, "objective"]
]

#config for the text regression
text_regression_config = [
    [":metric", ":metric_evalml_text_regression", [":log_loss"], "single_value", "dict", eval_metrics, "objective"]
]

#config for the time series forecasting
time_series_forecasting_config = [
    [":metric", ":metric_evalml_time_series_regression", [":log_loss"], "single_value", "dict", eval_metrics, "objective"]
]

# dictionary for mapping the selected task to the appropriate config
task_config = {
    ":tabular_classification": tabular_classification_config,
    ":tabular_regression": tabular_regression_config,
    ":text_classification": text_classification_config,
    ":text_regression": text_regression_config,
    ":time_series_forecasting" :time_series_forecasting_config
}

# dictionary for mapping the selected task to the appropriate config
task_config_binary_metric = {
    ":tabular_classification": tabular_classification_config_binary_metrics,
    ":tabular_regression": tabular_regression_config,
    ":text_classification": text_classification_config_binary_metrics,
    ":text_regression": text_regression_config,
    ":time_series_forecasting" :time_series_forecasting_config
}


