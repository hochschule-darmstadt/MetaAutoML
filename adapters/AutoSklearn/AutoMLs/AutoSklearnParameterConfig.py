import autosklearn.metrics

#lookup dictionary for AutoSklearn metrics values
#https://automl.github.io/auto-sklearn/master/api.html#classification-metrics
#https://automl.github.io/auto-sklearn/master/api.html#regression-metrics
autosklearn_metrics = {
    #classification
    ":accuracy": autosklearn.metrics.accuracy,
    ":balanced_accuracy": autosklearn.metrics.balanced_accuracy,
    ":f_measure": autosklearn.metrics.f1,
    ":f1_macro": autosklearn.metrics.f1_macro,
    ":f1_micro": autosklearn.metrics.f1_micro,
    ":f1_samples": autosklearn.metrics.f1_samples,
    ":f1_weighted": autosklearn.metrics.f1_weighted,
    ":receiver_operating_characteristic_curve": autosklearn.metrics.roc_auc,
    ":precision": autosklearn.metrics.precision,
    ":precision_macro": autosklearn.metrics.precision_macro,
    ":precision_micro": autosklearn.metrics.precision_micro,
    ":precision_samples": autosklearn.metrics.precision_samples,
    ":precision_weighted": autosklearn.metrics.precision_weighted,
    ":average_precision": autosklearn.metrics.average_precision,
    ":recall": autosklearn.metrics.recall,
    ":recall_macro": autosklearn.metrics.recall_macro,
    ":recall_micro": autosklearn.metrics.recall_micro,
    ":recall_samples": autosklearn.metrics.recall_samples,
    ":recall_weighted": autosklearn.metrics.recall_weighted,
    ":log_loss": autosklearn.metrics.log_loss,

    #regression
    ":r2": autosklearn.metrics.r2,
    ":mean_squared_error": autosklearn.metrics.mean_squared_error,
    ":mean_absolute_error": autosklearn.metrics.mean_absolute_error,
    ":median_absolute_error": autosklearn.metrics.median_absolute_error
}


parameters = {
    #tabular classification
    ":time_limit_autosklearn_tabular_classification": {
                                                    "parameter_name": "time_left_for_this_task"
                                                },
    ":time_limit_per_run_autosklearn_tabular_classification": {
                                                    "parameter_name": "per_run_time_limit"
                                                },
    ":ensemble_size_autosklearn_tabular_classification": {
                                                    "parameter_name": "ensemble_size"
                                                },
    ":ensemble_nbest_autosklearn_tabular_classification": {
                                                    "parameter_name": "ensemble_nbest"
                                                },
    ":metric_autosklearn_tabular_classification": {
                                                    "parameter_name": "metric",
                                                    "lookup_dict": autosklearn_metrics
                                                },
    ":use_approach_autosklearn_tabular_classification": {
                                                    "parameter_name": "include_estimators"
                                                },
    ":include_preprocessor_autosklearn_tabular_classification": {
                                                    "parameter_name": "include_preprocessors"
                                                },
    #tabular regression
    ":time_limit_autosklearn_tabular_regression": {
                                                    "parameter_name": "time_left_for_this_task"
                                                },
    ":time_limit_per_run_autosklearn_tabular_regression": {
                                                    "parameter_name": "per_run_time_limit"
                                                },
    ":ensemble_size_autosklearn_tabular_regression": {
                                                    "parameter_name": "ensemble_size"
                                                },
    ":ensemble_nbest_autosklearn_tabular_regression": {
                                                    "parameter_name": "ensemble_nbest"
                                                },
    ":metric_autosklearn_tabular_regression": {
                                                    "parameter_name": "metric",
                                                    "lookup_dict": autosklearn_metrics
                                                },
    ":use_approach_autosklearn_tabular_regression": {
                                                    "parameter_name": "include_estimators"
                                                },
    ":include_preprocessor_autosklearn_tabular_regression": {
                                                    "parameter_name": "include_preprocessors"
                                                }
}
