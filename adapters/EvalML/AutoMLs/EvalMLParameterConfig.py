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

eval_use_approach = {
    #":": "BASELINE",
    ":catboost": "CATBOOST",
    ":decision_tree": "DECISION_TREE",
    #":": "ENSEMBLE",
    ":extra_tree": "EXTRA_TREES",
    #":": "K_NEIGHBORS",
    ":light_gradient_boosting_machine": "LIGHTGBM",
    ":linear_regression": "LINEAR_MODEL",
    #":": "NONE",
    ":random_forest": "RANDOM_FOREST",
    #":": "SVM",
    ":xgboost": "XGBOOST"
}

eval_tuner = {
    ":random": "RandomSearchTuner",
    ":grid_search": "GridSearchTuner",
    ":skopt": "SKOptTuner"
}

eval_featurizers = {
    ":datetime_featurizer" : "DatetimeFeaturizer",
    ":email_featurizer" : "EmailFeaturizer",
    ":url_featurizer" : "URLFeaturizer",
    ":natural_language_featurizer" : "NaturalLanguageFeaturizer",
    ":time_series_featurizer" : "TimeSeriesFeaturizer"
}


parameters = {
#general parameters
    ":tuner_class_evalml": {
                                                    "parameter_name": "",
                                                    "lookup_dict": eval_tuner
                                                },
    ":optimize_thresholds_evalml": {
                                                    "parameter_name": "optimize_thresholds"
                                                },
    ":ensembling_evalml": {
                                                    "parameter_name": "ensembling"
                                                },
    ":max_batches_evalml": {
                                                    "parameter_name": "max_batches"
                                                },
    ":allow_long_running_models_evalml": {
                                                    "parameter_name": "allow_long_running_models"
                                                },
    ":pipelines_per_batch_evalml": {
                                                    "parameter_name": "_pipelines_per_batch"
                                                },
    ":exclude_featurizers_evalml": {
                                                    "parameter_name": "exclude_featurizers",
                                                    "lookup_dict": eval_featurizers
                                                },
    #tabular classification
    ":use_approach_evalml_tabular_classification": {
                                                    "parameter_name": "allowed_model_families",
                                                    "lookup_dict": eval_use_approach
                                                },
    ":metric_evalml_tabular_classification": {
                                                    "parameter_name": "objective",
                                                    "lookup_dict": eval_metrics
                                                },
    #tabular regression
    ":use_approach_evalml_tabular_regression": {
                                                    "parameter_name": "allowed_model_families",
                                                    "lookup_dict": eval_use_approach
                                                },
    ":metric_evalml_tabular_regression": {
                                                    "parameter_name": "objective",
                                                    "lookup_dict": eval_metrics
                                                },

    #time series regression
    ":use_approach_evalml_time_series_regression": {
                                                    "parameter_name": "allowed_model_families",
                                                    "lookup_dict": eval_use_approach
                                                },
    ":metric_evalml_time_series_regression": {
                                                    "parameter_name": "objective",
                                                    "lookup_dict": eval_metrics
                                                },
    ":forecasting_horizon_evalml_time_series_forcasting": {
                                                    "parameter_name": "forecast_horizon",
                                                    "default": [1]
                                                },
    ":lookback_evalml_time_series_forecasting": {
                                                    "parameter_name": "max_delay",
                                                    "default": [1]
                                                },
    ":gap_evalml_time_series_forecasting": {
                                                    "parameter_name": "gap",
                                                    "default": [1]
                                                },

    #text classification
    ":use_approach_evalml_text_classification": {
                                                    "parameter_name": "allowed_model_families",
                                                    "lookup_dict": eval_use_approach
                                                },
    ":metric_evalml_text_classification": {
                                                    "parameter_name": "objective",
                                                    "lookup_dict": eval_metrics
                                                },
     #text regression
    ":use_approach_evalml_text_regression": {
                                                    "parameter_name": "allowed_model_families",
                                                    "lookup_dict": eval_use_approach
                                                },
    ":metric_evalml_text_regression": {
                                                    "parameter_name": "objective",
                                                    "lookup_dict": eval_metrics
                                                }
}

parametersBinary = {
#general parameters
    ":tuner_class_evalml": {
                                                    "parameter_name": "",
                                                    "lookup_dict": eval_tuner
                                                },
    ":optimize_thresholds_evalml": {
                                                    "parameter_name": "optimize_thresholds"
                                                },
    ":ensembling_evalml": {
                                                    "parameter_name": "ensembling"
                                                },
    ":max_batches_evalml": {
                                                    "parameter_name": "max_batches"
                                                },
    ":allow_long_running_models_evalml": {
                                                    "parameter_name": "allow_long_running_models"
                                                },
    ":pipelines_per_batch_evalml": {
                                                    "parameter_name": "_pipelines_per_batch"
                                                },
    ":exclude_featurizers_evalml": {
                                                    "parameter_name": "exclude_featurizers",
                                                    "lookup_dict": eval_featurizers
                                                },
    #tabular classification
    ":use_approach_evalml_tabular_classification": {
                                                    "parameter_name": "allowed_model_families",
                                                    "lookup_dict": eval_use_approach
                                                },
    ":metric_evalml_tabular_classification": {
                                                    "parameter_name": "objective",
                                                    "lookup_dict": eval_metrics_binary
                                                },
    #tabular regression
    ":use_approach_evalml_tabular_regression": {
                                                    "parameter_name": "allowed_model_families",
                                                    "lookup_dict": eval_use_approach
                                                },
    ":metric_evalml_tabular_regression": {
                                                    "parameter_name": "objective",
                                                    "lookup_dict": eval_metrics_binary
                                                },

    #time series regression
    ":use_approach_evalml_time_series_regression": {
                                                    "parameter_name": "allowed_model_families",
                                                    "lookup_dict": eval_use_approach
                                                },
    ":metric_evalml_time_series_regression": {
                                                    "parameter_name": "objective",
                                                    "lookup_dict": eval_metrics_binary
                                                },
    ":forecasting_horizon_evalml_time_series_forcasting": {
                                                    "parameter_name": "forecast_horizon",
                                                    "default": [1]
                                                },
    ":lookback_evalml_time_series_forecasting": {
                                                    "parameter_name": "max_delay",
                                                    "default": [1]
                                                },
    ":gap_evalml_time_series_forecasting": {
                                                    "parameter_name": "gap",
                                                    "default": [1]
                                                },

    #text classification
    ":use_approach_evalml_text_classification": {
                                                    "parameter_name": "allowed_model_families",
                                                    "lookup_dict": eval_use_approach
                                                },
    ":metric_evalml_text_classification": {
                                                    "parameter_name": "objective",
                                                    "lookup_dict": eval_metrics_binary
                                                },
     #text regression
    ":use_approach_evalml_text_regression": {
                                                    "parameter_name": "allowed_model_families",
                                                    "lookup_dict": eval_use_approach
                                                },
    ":metric_evalml_text_regression": {
                                                    "parameter_name": "objective",
                                                    "lookup_dict": eval_metrics_binary
                                                }
}
