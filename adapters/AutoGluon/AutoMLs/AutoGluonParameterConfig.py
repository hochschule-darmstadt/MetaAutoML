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
    #":": "mean_wQuantileLoss",      #currently no metric in ontology
    ":mean_absolute_percentage_error": "MAPE",
    ":symmetric_mean_absolute_percentage_error": "sMAPE",
    ":mean_absolute_scaled_error": "MASE",
    ":mean_squared_error": "MSE",
    ":rooted_mean_squared_error": "RMSE"
}

parameters = {
#general
# NOTE_: Not found in documentation of autogluon
    #":use_approach_autogluon_classification": {
    #                                                "parameter_name": "",
    #                                                "lookup_dict":
    #                                            },
    #":use_approach_autogluon_regression": {
    #                                                "parameter_name": "",
    #                                                "lookup_dict":
    #                                            },

    #tabular classification
    ":metric_autogluon_tabular_classification": {
                                                    "parameter_name": "eval_metric",
                                                    "lookup_dict": autogluon_metrics
                                                },

    #tabular regression
    ":metric_autogluon_tabular_regression": {
                                                    "parameter_name": "eval_metric",
                                                    "lookup_dict": autogluon_metrics
                                                },

    #time series forecasting
    ":metric_autogluon_time_series_forecasting": {
                                                    "parameter_name": "eval_metric",
                                                    "lookup_dict": autogluon_time_series_metrics
                                                },
    ":metric_autogluon_time_series_forecasting": {
                                                    "parameter_name": "prediction_length",
                                                    "default": [1]
                                                },

    #image classification
    ":metric_autogluon_image_classification": {
                                                    "parameter_name": "eval_metric",
                                                    "lookup_dict": autogluon_metrics
                                                },

    #text classification
    ":metric_autogluon_text_classification": {
                                                    "parameter_name": "eval_metric",
                                                    "lookup_dict": autogluon_metrics
                                                },

    #text regression
    ":metric_autogluon_text_regression": {
                                                    "parameter_name": "eval_metric",
                                                    "lookup_dict": autogluon_metrics
                                                },

    #named entity recognition
    ":metric_auto_gluon_named_entity_recognition": {
                                                    "parameter_name": "eval_metric",
                                                    "lookup_dict": autogluon_metrics
                                                },

    #object detection
}
