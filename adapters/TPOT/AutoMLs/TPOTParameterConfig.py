#lookup dictionary for TPOT metrics values
#http://epistasislab.github.io/tpot/api/#classification
#http://epistasislab.github.io/tpot/api/#regression
tpot_metrics = {
    #classification
    ":accuracy": "accuracy",
    ":average_precision": "average_precision",
    ":adjusted_rand_score": "adjusted_rand_score",
    ":balanced_accuracy": "balanced_accuracy",
    ":f_measure": "f1",
    ":f_measure_macro": "f1_macro",
    ":f_measure_micro": "f1_micro",
    ":f_measure_samples": "f1_samples",
    ":f_measure_weighted": "f1_weighted",
    ":log_loss": "neg_log_loss",
    ":precision": "precision",
    ":precision_macro": "precision_macro",
    ":precision_micro": "precision_micro",
    ":precision_samples": "precision_samples",
    ":precision_weighted": "precision_weighted",
    ":recall": "recall",
    ":recall_macro": "recall_macro",
    ":recall_micro": "recall_micro",
    ":recall_samples": "recall_samples",
    ":recall_weighted": "recall_weighted",
    ":jaccard": "jaccard",
    ":jaccard_macro": "jaccard_macro",
    ":jaccard_micro": "jaccard_micro",
    ":jaccard_samples": "jaccard_samples",
    ":jaccard_weighted": "jaccard_weighted",
    ":receiver_operating_characteristic_curve": "roc_auc",
    ":receiver_operating_characteristic_curve_one_vs_rest": "roc_auc_ovr",
    ":receiver_operating_characteristic_curve_one_vs_one": "roc_auc_ovo",
    ":receiver_operating_characteristic_curve_one_vs_rest_weighted": "roc_auc_ovr_weighted",
    ":receiver_operating_characteristic_curve_one_vs_one_weighted": "roc_auc_ovo_weighted",

    #regression
    ":median_absolute_error": "neg_median_absolute_error",
    ":mean_absolute_error": "neg_mean_absolute_error",
    ":mean_squared_error": "neg_mean_squared_error",
    ":r2": "r2"
}

#configs for the different tasks that can be executed with TPOT
#each parameter has its own line that contains:
#the broader type of the parameter(broader id); the autoML specific parameter id; the default value in case no parameter-value is selected;
#the expected amount of the parameters(single_value/list); the type to which it should be converted (integer/dictionary); the lookup dictionary which includes the converting types;
#the autoML function parameter names
#[broader_type, specific_type, default, expected parameter 'count', converting type, lookup dictionary, used name by autoML]

#config for the tabular classification
tabular_classification_config = [
    [":metric", ":metric_tpot_tabular_classification", [":accuracy"], "single_value", "dict", tpot_metrics, "scoring"]
]

#config for the tabular regression
tabular_regression_config = [
    [":metric", ":metric_tpot_tabular_regression", [":mean_squared_error"], "single_value", "dict", tpot_metrics, "scoring"]
]

#config for the image classification
image_classification_config = [
    [":metric", ":metric_tpot_image_classification", [":accuracy"], "single_value", "dict", tpot_metrics, "scoring"]
]

# dictionary for mapping the selected task to the appropriate config
task_config = {
    ":tabular_classification": tabular_classification_config,
    ":tabular_regression": tabular_regression_config,
    ":image_classification": image_classification_config
}
