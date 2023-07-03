#lookup dictionary for LAMA metrics values
# https://lightautoml.readthedocs.io/en/latest/pages/modules/generated/lightautoml.tasks.base.Task.html#lightautoml.tasks.base.Task
lama_metrics = {
#classification - only multi-tabulaclassification is implemented
    ":categorical_cross_entropy": "crossentropy",
    ":area_under_roc_curve": "auc",
   
    #regression
    ":mean_absolute_percentage_error": "mape",
    ":mean_absolute_error": "mae",
    ":mean_squared_error": "mse",
    ":rooted_mean_squared_log_error": "rmsle"
}
lama_lossfunction = {
#classification
    ":categorical_cross_entropy": "crossentropy",
    ":f_measure": "f1",

   
    #regression
    ":mean_absolute_percentage_error": "mape",
    ":mean_absolute_error": "mae",
    ":mean_squared_error": "mse",
    ":rooted_mean_squared_log_error": "rmsle"
}




#configs for the different tasks that can be executed with LAMA
#each parameter has its own line that contains:
#the broader type of the parameter(broader id); the autoML specific parameter id; the default value in case no parameter-value is selected;
#the expected amount of the parameters(single_value/list); the type to which it should be converted (integer/dictionary); the lookup dictionary which includes the converting types;
#the autoML function parameter names
#[broader_type, specific_type, default, expected parameter 'count', converting type, lookup dictionary, used name by autoML]

#config for the tabular classification
tabular_classification_config = [
    [":metric", ":metric_lama_tabular_classification", [":categorical_cross_entropy"], "single_value", "dict", lama_metrics, "metric"],
    [":loss", ":loss_lama_tabular_classification", [":categorical_cross_entropy"], "single_value", "dict", lama_lossfunction, "loss"],
]


#config for the tabular regression
tabular_regression_config = [
    [":metric", ":metric_lama_tabular_regression", [":mse"], "single_value", "dict", lama_metrics, "metric"],
    [":loss", ":loss_lama_tabular_regression", [":mse"], "single_value", "dict", lama_lossfunction, "loss"],
]





# dictionary for mapping the selected task to the appropriate config
task_config = {
    ":tabular_classification": tabular_classification_config,
    ":tabular_regression": tabular_regression_config,
}




