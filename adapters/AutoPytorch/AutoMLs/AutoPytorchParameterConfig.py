#lookup dictionary for AutoPytorch metrics values
#https://github.com/automl/Auto-PyTorch/blob/master/autoPyTorch/pipeline/components/training/metrics/metrics.py
autopytorch_metrics = {
    #classification
    ":accuracy": "accuracy",
    ":balanced_accuracy": "balanced_accuracy",
    ":f_measure": "f1",
    ":roc_auc": "roc_auc",
    ":average_precision": "average_precision",
    ":precision": "precision",
    ":recall": "recall",
    ":log_loss": "log_loss",

    #regression
    ":mean_absolute_error": "mean_absolute_error",
    ":mean_squared_error": "mean_squared_error",
    ":rooted_mean_squared_error": "root_mean_squared_error",
    ":mean_squared_log_error ": "mean_squared_log_error",
    ":median_absolute_error ": "median_absolute_error",
    ":r2": "r2"
}

#Autopytorch reuses the normal regression metrics but renamed them for forecasting
autopytorch_ts_forecasting_metrics = {
    #regression TS forecasting
    ":mean_absolute_error": "mean_MAE_forecasting",
    ":median_absolute_error": "median_MAE_forecasting",
    ":mean_absolute_percentage_error": "mean_MAPE_forecasting",
    ":median_absolute_percentage_error": "median_MAPE_forecasting",
    ":mean_squared_error": "mean_MSE_forecasting",
    ":median_squared_error": "median_MSE_forecasting"
}

parameters = {
    #tabular classification
    ":metric_autopytorch_tabular_classification": {
                                                    "parameter_name": "optimize_metric",
                                                    "lookup_dict": autopytorch_metrics
                                                },
    #tabular regression
    ":metric_autopytorch_tabular_regression": {
                                                    "parameter_name": "optimize_metric",
                                                    "lookup_dict": autopytorch_metrics
                                                },
    #time_series_forcasting
    ":metric_autopytorch_time_series_forcasting": {
                                                    "parameter_name": "optimize_metric",
                                                    "lookup_dict": autopytorch_ts_forecasting_metrics
                                                },
    ":forecasting_horizon": {
                                                    "parameter_name": "n_prediction_steps",
                                                    "default": [1]
                                                }
}
