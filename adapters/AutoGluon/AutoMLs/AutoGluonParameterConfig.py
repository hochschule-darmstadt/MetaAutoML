#lookup dictionary for AutoGluon metrics values
#https://auto.gluon.ai/stable/api/autogluon.predictor.htm
#https://auto.gluon.ai/stable/_modules/autogluon/text/text_prediction/predictor.html#TextPredictor
autogluon_metrics = {
    #classification
    ":accuracy": "accuracy",
    ":balanced_accuracy": "balanced_accuracy",
    ":f_measure": "f1",
    ":f_measure_macro": "f1_macro",
    ":f_measure_micro": "f1_micro",
    ":f_measure_weighted": "f1_weighted",
    ":receiver_operating_characteristic_curve": "roc_auc",
    ":receiver_operating_characteristic_curve_one_vs_one": "roc_auc_ovo_macro",
    ":average_precision_score": "average_precision",
    ":precision": "precision",
    ":precision_macro": "precision_macro",
    ":precision_micro": "precision_micro",
    ":precision_weighted": "precision_weighted",
    ":recall": "recall",
    ":recall_macro": "recall_macro",
    ":recall_micro": "recall_micro",
    ":recall_weighted": "recall_weighted",
    ":log_loss": "log_loss",
    ":pac_score": "pac_score",

    #regression
    ":rooted_mean_squared_error": "root_mean_squared_error",
    ":mean_squared_error": "mean_squared_error",
    ":mean_absolute_error": "mean_absolute_error",
    ":median_absolute_error": "median_absolute_error",
    ":mean_absolute_percentage_error": "mean_absolute_percentage_error",
    ":r2": "r2",
    ":spearman_rank_correlation_coefficient": "spearmanr",
    ":pearson_correlation_coefficient": "pearsonr"
}

#extra dictionary for time series because they changed the acronym which they want for the metric -.-
autogluon_time_series_metrics = {
    #time series
    ":": "mean_wQuantileLoss",      #currently no metric in ontology
    ":mean_absolute_percentage_error": "MAPE",
    ":symmetric_mean_absolute_percentage_error": "sMAPE",
    ":mean_absolute_scaled_error": "MASE",
    ":mean_squared_error": "MSE",
    ":rooted_mean_squared_error": "RMSE"
}

#configs for the different tasks that can be executed with AutoGluon
#each parameter has its own line that contains:
#the broader type of the parameter(broader id); the autoML specific parameter id; the default value in case no parameter-value is selected;
#the expected amount of the parameters(single_value/list); the type to which it should be converted (integer/dictionary); the lookup dictionary which includes the converting types;
#the autoML function parameter names
#[broader_type, specific_type, default, expected parameter 'count', converting type, lookup dictionary, used name by autoML]

#config for the tabular classification
tabular_classification_config = [
    [":metric", ":metric_autogluon_tabular_classification", [":accuracy"], "single_value", "dict", autogluon_metrics, "eval_metric"]
]

#config for the tabular regression
tabular_regression_config = [
    [":metric", ":metric_autogluon_tabular_regression", [":rooted_mean_squared_error"], "single_value", "dict", autogluon_metrics, "eval_metric"]
]

#config for the text classification
text_classification_config = [
    [":metric", ":metric_autogluon_text_classification", [":accuracy"], "single_value", "dict", autogluon_metrics, "eval_metric"]
]

#config for the image classification
image_classification_config = [
    [":metric", ":metric_autogluon_image_classification", [":accuracy"], "single_value", "dict", autogluon_metrics, "eval_metric"]
]

#config for the time series forecasting
time_series_forecasting_config = [
    [":metric", ":metric_autogluon_time_series_forecasting", [None], "single_value", "dict", autogluon_time_series_metrics, "eval_metric"]    #std: mean_wQuantileLoss
]


# dictionary for mapping the selected task to the appropriate config
task_config = {
    ":tabular_classification": tabular_classification_config,
    ":tabular_regression": tabular_regression_config,
    ":text_classification": text_classification_config,
    ":image_classification": image_classification_config,
    ":time_series_forecasting" :time_series_forecasting_config
}
