#lookup dictionary for EvalML metrics values
# https://openml-labs.github.io/gama/master/api/index.html
gama_metrics = {
#classification
    ":accuracy": "accuracy",
    ":average_precision": "average_precision",
    ":f_measure_macro": "f1_macro",
    ":f_measure_micro": "f1_micro",
    ":f_measure_samples": "f1_samples",
    ":f_measure_weighted": "f1_weighted",
    ":neg_log_loss": "neg_log_loss",
    ":precision_macro": "precision_macro",
    ":precision_micro": "precision_micro",
    ":precision_samples": "precision_samples",
    ":precision_weighted": "precision_weighted",
    ":recall_macro": "recall_macro",
    ":recall_micro": "recall_micro",
    ":recall_samples": "recall_samples",
    ":recall_weighted": "recall_weighted",
    ":receiver_operating_characteristic_curve": "roc_auc",
   
    #regression
    ":explained_variance": "explained_variance",
    ":median_absolute_error": "neg_median_absolute_error",
    ":mean_absolute_error": "neg_mean_absolute_error",
    ":mean_squared_error": "neg_mean_squared_error",
    ":r2": "r2",
    ":mean_squared_log_error": "neg_median_absolute_error"
}




#configs for the different tasks that can be executed with GAMA
#each parameter has its own line that contains:
#the broader type of the parameter(broader id); the autoML specific parameter id; the default value in case no parameter-value is selected;
#the expected amount of the parameters(single_value/list); the type to which it should be converted (integer/dictionary); the lookup dictionary which includes the converting types;
#the autoML function parameter names
#[broader_type, specific_type, default, expected parameter 'count', converting type, lookup dictionary, used name by autoML]

#config for the tabular classification
tabular_classification_config = [
    [":metric", ":metric_gama_tabular_classification", [":neg_log_loss"], "list", "dict", gama_metrics, "scoring"],
]


#config for the tabular regression
tabular_regression_config = [
    [":metric", ":metric_evalml_tabular_regression", [":explained_variance"], "list", "dict", gama_metrics, "scoring"]
]





# dictionary for mapping the selected task to the appropriate config
task_config = {
    ":tabular_classification": tabular_classification_config,
    ":tabular_regression": tabular_regression_config,
}




