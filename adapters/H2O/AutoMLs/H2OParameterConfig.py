#
# This Class contains the configuration objects for the H2OAdapter
#

#max_runtime_secs
#max_models
#stopping_metric
#sort_metric
#include_algos/exclude_algos

h2o_metrics = {
    #regression
    ":mean_absolute_error": "MAE",
    ":mean_residual_deviance": "deviance",
    ":mean_squared_error": "MSE",
    ":root_mean_squared_error": "RMSE",
    ":root_mean_squared_log_error": "RMSLE",

    #classification
    #h2o is using MSE for classification and for regression
    ":accuracy": "misclassification",
    ":area_under_roc_curve": "AUC",
    ":area_under_precision_recall_curve" : "AUCPR",
    ":log_loss": "logloss",
    ":mean_per_class_error": "mean_per_class_error",
    ":mean_squared_error": "MSE",

    #lift_top_group - not implemented
}

# supported algorithms by h2o
h2o_algorithms = {
    ":distributed_random_forest": "DRF",
    ":artificial_neural_network": "DeepLearning",
    ":gradient_boosting_tree": ["GBM", "XGBoost"],
    ":stacking_ensemble": "StackedEnsemble",
    #GLM - not implemented - regression algorithms
}

parameters = {
    #tabular classification
    ":metric_h2o_automl_tabular_classification": {
        "parameter_name": "stopping_metric",
        "lookup_dict": h2o_metrics,
    },
    # tabular regression
    ":metric_h2o_automl_tabular_regression": {
        "parameter_name": "stopping_metric",
        "lookup_dict": h2o_metrics,
    },
    #general
    ":include_approach_h2o_automl": {
        "parameter_name": "include_algos",
        "lookup_dict": h2o_algorithms,
    },
    ":max_models_h2o_automl": {
        "parameter_name": "max_models",
    },
    #determines how the best model is selected
    ":sort_metric_h2o_automl": {
        "parameter_name": "sort_metric",
        "lookup_dict": h2o_metrics,
    }
}
