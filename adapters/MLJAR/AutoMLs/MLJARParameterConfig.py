#lookup dictionary for mljar metrics values
#https://supervised.mljar.com/api/  !!Warning!! Looks like the documentation is outdated
#https://github.com/mljar/mljar-supervised/blob/master/supervised/utils/additional_metrics.py
mljar_metrics = {
    ":log_loss": "logloss",
    ":area_under_roc_curve": "auc",
    ":f_measure": "f1",
    ":accuracy": "accuracy",
    ":precision": "precision",
    ":recall": "recall",
    ":matthews_correlation_coefficient": "mcc",

    #regression
    ":rooted_mean_squared_error": "RMSE",
    ":mean_absolute_error": "MAE",
    ":mean_squared_error": "MSE",
    ":r2": "R2",
    ":mean_absolute_percentage_error": "MAPE"
}

parameters = {
    #tabular classification
    ":metric_mljar_tabular_classification": {
                                                    "parameter_name": "eval_metric",
                                                    "lookup_dict": mljar_metrics
                                                },
    #tabular regression
    ":metric_mljar_tabular_regression": {
                                                    "parameter_name": "eval_metric",
                                                    "lookup_dict": mljar_metrics
                                                }
}
