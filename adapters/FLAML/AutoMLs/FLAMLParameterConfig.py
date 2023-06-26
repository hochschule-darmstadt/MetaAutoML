#lookup dictionary for FLAML metrics values
#https://microsoft.github.io/FLAML/docs/Use-Cases/task-oriented-automl
#https://github.com/microsoft/FLAML/blob/main/flaml/automl/ml.py
flaml_metrics = {
    #classification
    ":accuracy": "accuracy",
    ":log_loss": "log_loss",
    ":receiver_operating_characteristic_curve": "roc_auc",
    ":receiver_operating_characteristic_curve_one_vs_rest": "roc_auc_ovr",
    ":receiver_operating_characteristic_curve_one_vs_one": "roc_auc_ovo",
    ":average_precision_score": "ap",
    ":f_measure": "f1",
    ":f_measure_micro": "micro_f1",
    ":f_measure_macro": "macro_f1",
    ":area_under_roc_curve_weighted": "roc_auc_weighted",
    ":receiver_operating_characteristic_curve_one_vs_rest_weighted": "roc_auc_ovr_weighted",
    ":receiver_operating_characteristic_curve_one_vs_one_weighted": "roc_auc_ovo_weighted",

    #regression
    ":rooted_mean_squared_error": "rmse",
    ":mean_squared_error": "mse",
    ":mean_absolute_error": "mae",
    ":mean_absolute_percentage_error": "mape",
    ":r2": "r2",

    #ranking
    ":normalized_discounted_cumulative_gain": "ndcg",
    #":": "ndcg@k"    #not in onology metrics
}

#lookup dictionary for FLAML use approach values
#https://microsoft.github.io/FLAML/docs/Use-Cases/task-oriented-automl#estimator-and-search-space
flaml_use_approaches = {
":auto": "auto",
":light_gradient_boosting_machine": "lgbm",
":xgboost": "xgboost",
#"": "xgb_limitdepth",
":random_forest": "rf",
":extra_tree": "extra_tree",
":logistic_regression": "lrl1",
#":logistic_regression": "lrl2",
":catboost": "catboost",
":k_nearest_neighbor": "kneighbor",
":prophet": "prophet",
":autoregressive_integrated_moving_average": "arima",
":seasonal_autoregressive_integrated_moving_average_exogenous": "sarimax",
":transformer": "transformer",
":temporal_fusion_transformer": "temporal_fusion_transformer"
}

#ToDo:
#lookup dictionary for FLAML tuner values
#https://microsoft.github.io/FLAML/docs/Use-Cases/Tune-User-Defined-Function/#hyperparameter-optimization-algorithm
flaml_tuner = {
":auto_optimization_approach": "auto",
":frugal_optimization_for_costrelated_hyperparameters": "cfo",
":blendsearch": "bs"
}

flaml_split_type = {
":auto_split": "auto",
":stratified": "stratified",
":uniform": "uniform",
":time": "time",
":group": "group",
}

flaml_eval_method = {
":auto_evaluation": "auto",
":cross_validation": "cv",
":holdout": "holdout"
}

parameters = {
    #tabular classification
    ":use_approach_flaml_tabular_classification": {
                                                    "parameter_name": "estimator_list",
                                                    "lookup_dict": flaml_use_approaches
                                                },
    ":metric_flaml_tabular_classification": {
                                                    "parameter_name": "metric",
                                                    "lookup_dict": flaml_metrics
                                                },
    ":ensemble_flaml_tabular_classification": {
                                                    "parameter_name": "ensemble"
                                                },
    ":eval_method_flaml": {
                                                    "parameter_name": "eval_method",
                                                    "lookup_dict": flaml_eval_method
                                                },
    ":validation_split_flaml": {
                                                    "parameter_name": "split_ratio"
                                                },
    ":cross_validation_fold_flaml": {
                                                    "parameter_name": "n_splits"
                                                },
    ":split_type_flaml_classification": {
                                                    "parameter_name": "split_type",
                                                    "lookup_dict": flaml_split_type
                                                },
    ":hyperparameter_optimization_method_flaml": {
                                                    "parameter_name": "hpo_method",
                                                    "lookup_dict": flaml_tuner
                                                },

    #tabular regression
    ":use_approach_flaml_tabular_regression": {
                                                    "parameter_name": "estimator_list",
                                                    "lookup_dict": flaml_use_approaches
                                                },
    ":metric_flaml_tabular_regression": {
                                                    "parameter_name": "metric",
                                                    "lookup_dict": flaml_metrics
                                                },
    ":ensemble_flaml_tabular_regression": {
                                                    "parameter_name": "ensemble"
                                                },
    ":split_type_flaml_regression": {
                                                    "parameter_name": "split_type",
                                                    "lookup_dict": flaml_split_type
                                                },
    #time series forecasting
    ":use_approach_flaml_time_series_analysis": {
                                                    "parameter_name": "estimator_list",
                                                    "lookup_dict": flaml_use_approaches
                                                },
    ":metric_flaml_time_series_analysis": {
                                                    "parameter_name": "metric",
                                                    "lookup_dict": flaml_metrics
                                                },
    ":ensemble_flaml_time_series_forecasting": {
                                                    "parameter_name": "ensemble"
                                                },
    ":forecasting_horizon_flaml_time_series_forcasting": {
                                                    "parameter_name": "period",
                                                    "default": [1]
                                                },
    ":split_type_flaml_time_series_forecasting": {
                                                    "parameter_name": "split_type",
                                                    "lookup_dict": flaml_split_type
                                                },
    #text classification
    ":use_approach_flaml_text_classification": {
                                                    "parameter_name": "estimator_list",
                                                    "lookup_dict": flaml_use_approaches
                                                },
    ":metric_flaml_text_classification": {
                                                    "parameter_name": "metric",
                                                    "lookup_dict": flaml_metrics
                                                },
    ":ensemble_flaml_text_classification": {
                                                    "parameter_name": "ensemble"
                                                },
    ":split_type_flaml_classification": {
                                                    "parameter_name": "split_type",
                                                    "lookup_dict": flaml_split_type
                                                },
    #text classification
    ":use_approach_flaml_text_regression": {
                                                    "parameter_name": "estimator_list",
                                                    "lookup_dict": flaml_use_approaches
                                                },
    ":metric_flaml_text_regression": {
                                                    "parameter_name": "metric",
                                                    "lookup_dict": flaml_metrics
                                                },
    ":ensemble_flaml_text_regression": {
                                                    "parameter_name": "ensemble"
                                                },
    ":split_type_flaml_regression": {
                                                    "parameter_name": "split_type",
                                                    "lookup_dict": flaml_split_type
                                                },
    #ranking
    ":use_approach_flaml_ranking": {
                                                    "parameter_name": "estimator_list",
                                                    "lookup_dict": flaml_use_approaches
                                                },
    ":metric_flaml_ranking": {
                                                    "parameter_name": "metric",
                                                    "lookup_dict": flaml_metrics
                                                },
    ":ensemble_flaml_ranking": {
                                                    "parameter_name": "ensemble"
                                                },
    ":split_type_flaml_ranking": {
                                                    "parameter_name": "split_type",
                                                    "lookup_dict": flaml_split_type
                                                },
}

