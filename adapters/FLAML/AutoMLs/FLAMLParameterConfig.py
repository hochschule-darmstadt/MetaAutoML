#lookup dictionary for FLAML metrics values
#https://microsoft.github.io/FLAML/docs/Use-Cases/task-oriented-automl
#https://github.com/microsoft/FLAML/blob/main/flaml/automl/ml.py
flaml_metrics = {
    #classification
    ":accuracy": "accuracy",
    ":log_loss": "log_loss",
    ":receiver_operating_characteristic_curve": "roc_auc",
    ":receiver_operating_characteristic_curve_one_vs_rest": "roc_auc_ovr",
    ":receiver_operating_characteristic_curve_one_vs_one": "roc_auc_ovo",
    ":average_precision_score": "ap",
    ":f_measure": "f1",
    ":f_measure_micro": "micro_f1",
    ":f_measure_macro": "macro_f1",
    ":area_under_roc_curve_weighted": "roc_auc_weighted",
    ":": "roc_auc_ovr_weighted",    #not in onology metrics
    ":": "roc_auc_ovo_weighted",    #not in onology metrics

    #regression
    ":rooted_mean_squared_error": "rmse",
    ":mean_squared_error": "mse",
    ":mean_absolute_error": "mae",
    ":mean_absolute_percentage_error": "mape",
    ":coefficient_of_determination": "a",
    ":r2": "r2",

    #ranking
    ":normalized_discounted_cumulative_gain": "ndcg",
    ":": "ndcg@k"    #not in onology metrics
}

#configs for the different tasks that can be executed with FLAML
#each parameter has its own line that contains:
#the broader type of the parameter(broader id); the autoML specific parameter id; the default value in case no parameter-value is selected;
#the expected amount of the parameters(single_value/list); the type to which it should be converted (integer/dictionary); the lookup dictionary which includes the converting types;
#the autoML function parameter names
#[broader_type, specific_type, default, expected parameter 'count', converting type, lookup dictionary, used name by autoML]

#config for the tabular classification
tabular_classification_config = [
    [":metric", ":metric_flaml_tabular_classification", [":log_loss"], "single_value", "dict", flaml_metrics, "metric"]
]

#config for the tabular regression
tabular_regression_config = [
    [":metric", ":metric_flaml_tabular_regression", [":r2"], "single_value", "dict", flaml_metrics, "metric"]
]

#config for the time series forecasting
time_series_forecasting_config = [
    [":metric", ":metric_flaml_time_series_forecasting", [":log_loss"], "single_value", "dict", flaml_metrics, "metric"]
]

#config for the text classification
text_classification_config = [
    [":metric", ":metric_flaml_text_classification", [":log_loss"], "single_value", "dict", flaml_metrics, "metric"]
]

# dictionary for mapping the selected task to the appropriate config
task_config = {
    ":tabular_classification": tabular_classification_config,
    ":tabular_regression": tabular_regression_config,
    ":time_series_forecasting" :time_series_forecasting_config,
    ":text_classification": text_classification_config
}
