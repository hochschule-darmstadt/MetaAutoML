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
    ":receiver_operating_characteristic_curve_one_vs_rest_weighted": "roc_auc_ovr_weighted",
    ":receiver_operating_characteristic_curve_one_vs_one_weighted": "roc_auc_ovo_weighted",

    #regression
    ":rooted_mean_squared_error": "rmse",
    ":mean_squared_error": "mse",
    ":mean_absolute_error": "mae",
    ":mean_absolute_percentage_error": "mape",
    ":r2": "r2",

    #ranking
    ":normalized_discounted_cumulative_gain": "ndcg",
    #":": "ndcg@k"    #not in onology metrics
}

#lookup dictionary for FLAML use approach values
#https://microsoft.github.io/FLAML/docs/Use-Cases/task-oriented-automl#estimator-and-search-space
flaml_use_approaches = {
":auto": "auto",
":light_gradient_boosting_machine": "lgbm",
":xgboost": "xgboost",
#"": "xgb_limitdepth",
":random_forest": "rf",
":extra_tree": "extra_tree",
":logistic_regression": "lrl1",
#":logistic_regression": "lrl2",
":catboost": "catboost",
":k_nearest_neighbor": "kneighbor",
":prophet": "prophet",
":autoregressive_integrated_moving_average": "arima",
":seasonal_autoregressive_integrated_moving_average_exogenous": "sarimax",
":transformer": "transformer",
":temporal_fusion_transformer": "temporal_fusion_transformer"
}

#ToDo:
#lookup dictionary for FLAML tuner values
#https://microsoft.github.io/FLAML/docs/Use-Cases/Tune-User-Defined-Function/#hyperparameter-optimization-algorithm
flaml_tuner = {
":auto": "auto",
"": "cfo",
"": "bs"
}

#configs for the different tasks that can be executed with FLAML
#each parameter has its own line that contains:
#the broader type of the parameter(broader id); the autoML specific parameter id; the default value in case no parameter-value is selected;
#the expected amount of the parameters(single_value/list); the type to which it should be converted (integer/dictionary); the lookup dictionary which includes the converting types;
#the autoML function parameter names
#[broader_type, specific_type, default, expected parameter 'count', converting type, lookup dictionary, used name by autoML]

#config for the tabular classification
tabular_classification_config = [
    [":metric", ":metric_flaml_tabular_classification", [":log_loss"], "single_value", "dict", flaml_metrics, "metric"],
    [":use_approach", ":use_approach_flaml_tabular_classification", [":auto"], "list", "dict", flaml_use_approaches, "estimator_list"]
]

#config for the tabular regression
tabular_regression_config = [
    [":metric", ":metric_flaml_tabular_regression", [":r2"], "single_value", "dict", flaml_metrics, "metric"],
    [":use_approach", ":use_approach_flaml_tabular_regression", [":auto"], "list", "dict", flaml_use_approaches, "estimator_list"]
]

#config for the time series forecasting
time_series_forecasting_config = [
    [":metric", ":metric_flaml_time_series_forecasting", [":mean_squared_error"], "single_value", "dict", flaml_metrics, "metric"],
    [":use_approach", ":use_approach_flaml_time_series_analysis", [":auto"], "list", "dict", flaml_use_approaches, "estimator_list"]
]

#config for the text classification
text_classification_config = [
    [":metric", ":metric_flaml_text_classification", [":log_loss"], "single_value", "dict", flaml_metrics, "metric"],
    [":use_approach", ":use_approach_flaml_text_classification", [":auto"], "list", "dict", flaml_use_approaches, "estimator_list"]
]

# dictionary for mapping the selected task to the appropriate config
task_config = {
    ":tabular_classification": tabular_classification_config,
    ":tabular_regression": tabular_regression_config,
    ":time_series_forecasting" :time_series_forecasting_config,
    ":text_classification": text_classification_config
}
