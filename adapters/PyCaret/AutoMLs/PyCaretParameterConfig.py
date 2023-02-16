#lookup dictionary for PyCaret metrics values
#https://github.com/pycaret/pycaret/blob/master/pycaret/containers/metrics/classification.py
#https://github.com/pycaret/pycaret/blob/master/pycaret/containers/metrics/regression.py
#https://github.com/pycaret/pycaret/blob/b506391b2a3409de85e31e1ef367c8bf63b0c4d1/pycaret/containers/metrics/time_series.py
pycaret_metrics = {
    #classification
    ":accuracy": "Accuracy",
    ":area_under_roc_curve": "AUC",
    ":recall": "Recall",
    ":precision": "Precision",
    ":f_measure": "F1",
    ":cohens_kappa": "Kappa",
    ":matthews_correlation_coefficient": "MCC",

    #regression
    ":mean_absolute_error": "MAE",
    ":mean_squared_error": "MSE",
    ":rooted_mean_squared_error": "RMSE",
    ":r2": "R2",
    ":rooted_mean_squared_log_error": "RMSLE",
    ":mean_absolute_percentage_error": "MAPE",

    #time series forecasting
    ":mean_absolute_scaled_error": "MASE",
    ":rooted_mean_squared_scaled_error": "RMSSE",
    ":symmetric_mean_absolute_percentage_error": "SMAPE",
    ":coverage": "COVERAGE"
}

#configs for the different tasks that can be executed with PyCaret
#each parameter has its own line that contains:
#the broader type of the parameter(broader id); the autoML specific parameter id; the default value in case no parameter-value is selected;
#the expected amount of the parameters(single_value/list); the type to which it should be converted (integer/dictionary); the lookup dictionary which includes the converting types;
#the autoML function parameter names
#[broader_type, specific_type, default, expected parameter 'count', converting type, lookup dictionary, used name by autoML]

#config for the tabular classification
tabular_classification_config = [
    [":metric", ":metric_pycaret_tabular_classification", [":accuracy"], "single_value", "dict", pycaret_metrics, "optimize"]
]

#config for the tabular regression
tabular_regression_config = [
    [":metric", ":metric_pycaret_tabular_regression", [":r2"], "single_value", "dict", pycaret_metrics, "optimize"]
]

#config for the time series forecasting
time_series_forecasting_config = [
    [":metric", ":metric_pycaret_time_series_forecasting", [":log_loss"], "single_value", "dict", pycaret_metrics, "optimize"]
]

# dictionary for mapping the selected task to the appropriate config
task_config = {
    ":tabular_classification": tabular_classification_config,
    ":tabular_regression": tabular_regression_config,
    ":time_series_forecasting" :time_series_forecasting_config
}
