#lookup dictionary for PyCaret metrics values
#https://github.com/pycaret/pycaret/blob/master/pycaret/containers/metrics/classification.py
#https://github.com/pycaret/pycaret/blob/master/pycaret/containers/metrics/regression.py
#https://github.com/pycaret/pycaret/blob/b506391b2a3409de85e31e1ef367c8bf63b0c4d1/pycaret/containers/metrics/time_series.py
pycaret_metrics = {
    #classification
    ":accuracy": "Accuracy",
    ":area_under_roc_curve": "AUC",
    ":recall": "Recall",
    ":precision": "Precision",
    ":f_measure": "F1",
    ":cohens_kappa": "Kappa",
    ":matthews_correlation_coefficient": "MCC",

    #regression
    ":mean_absolute_error": "MAE",
    ":mean_squared_error": "MSE",
    ":rooted_mean_squared_error": "RMSE",
    ":r2": "R2",
    ":rooted_mean_squared_log_error": "RMSLE",
    ":mean_absolute_percentage_error": "MAPE",

    #time series forecasting
    ":mean_absolute_scaled_error": "MASE",
    ":rooted_mean_squared_scaled_error": "RMSSE",
    ":symmetric_mean_absolute_percentage_error": "SMAPE",
    ":coverage": "COVERAGE"
}

parameters = {
    #general
    ":cross_validation_fold_pycaret": {
                                                    "parameter_name": "fold"
                                                },
    #tabular classification
    ":metric_pycaret_tabular_classification": {
                                                    "parameter_name": "optimize",
                                                    "lookup_dict": pycaret_metrics
                                                },
    #tabular regression
    ":metric_pycaret_tabular_regression": {
                                                    "parameter_name": "optimize",
                                                    "lookup_dict": pycaret_metrics
                                                },
    #time series forecasting
    ":metric_pycaret_time_series_forecasting": {
                                                    "parameter_name": "optimize",
                                                    "lookup_dict": pycaret_metrics
                                                },
    ":forecasting_horizon_pycaret_time_series_forcasting": {
                                                    "parameter_name": "optimize",
                                                    "default": [1]
                                                }
}
