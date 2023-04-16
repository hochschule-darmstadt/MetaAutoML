import autosklearn.metrics

#lookup dictionary for AutoSklearn metrics values
#https://automl.github.io/auto-sklearn/master/api.html#classification-metrics
#https://automl.github.io/auto-sklearn/master/api.html#regression-metrics
autosklearn_metrics = {
    #classification
    ":accuracy": autosklearn.metrics.accuracy,
    ":balanced_accuracy": autosklearn.metrics.balanced_accuracy,
    ":f_measure": autosklearn.metrics.f1,
    ":f1_macro": autosklearn.metrics.f1_macro,
    ":f1_micro": autosklearn.metrics.f1_micro,
    ":f1_samples": autosklearn.metrics.f1_samples,
    ":f1_weighted": autosklearn.metrics.f1_weighted,
    ":receiver_operating_characteristic_curve": autosklearn.metrics.roc_auc,
    ":precision": autosklearn.metrics.precision,
    ":precision_macro": autosklearn.metrics.precision_macro,
    ":precision_micro": autosklearn.metrics.precision_micro,
    ":precision_samples": autosklearn.metrics.precision_samples,
    ":precision_weighted": autosklearn.metrics.precision_weighted,
    ":average_precision": autosklearn.metrics.average_precision,
    ":recall": autosklearn.metrics.recall,
    ":recall_macro": autosklearn.metrics.recall_macro,
    ":recall_micro": autosklearn.metrics.recall_micro,
    ":recall_samples": autosklearn.metrics.recall_samples,
    ":recall_weighted": autosklearn.metrics.recall_weighted,
    ":log_loss": autosklearn.metrics.log_loss,

    #regression
    ":r2": autosklearn.metrics.r2,
    ":mean_squared_error": autosklearn.metrics.mean_squared_error,
    ":mean_absolute_error": autosklearn.metrics.mean_absolute_error,
    ":median_absolute_error": autosklearn.metrics.median_absolute_error
}

#configs for the different tasks that can be executed with AutoSklearn
#each parameter has its own line that contains:
#the broader type of the parameter(broader id); the autoML specific parameter id; the default value in case no parameter-value is selected;
#the expected amount of the parameters(single_value/list); the type to which it should be converted (integer/dictionary); the lookup dictionary which includes the converting types;
#the autoML function parameter names
#[broader_type, specific_type, default, expected parameter 'count', converting type, lookup dictionary, used name by autoML]

#config for the tabular classification
tabular_classification_config = [
    [":metric", ":metric_autosklearn_tabular_classification", [":accuracy"], "single_value", "dict", autosklearn_metrics, "metric"]
]

#config for the tabular regression
tabular_regression_config = [
    [":metric", ":metric_autosklearn_tabular_regression", [":r2"], "single_value", "dict", autosklearn_metrics, "metric"]
]

# dictionary for mapping the selected task to the appropriate config
task_config = {
    ":tabular_classification": tabular_classification_config,
    ":tabular_regression": tabular_regression_config
}
