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

    #clustering TODO
}

# supported clustering approaches in PyCaret
clustering_approaches = {
    ":affinity_propagation": "ap",
    ":agglomerative_clustering": "hclust",
    ":balanced_iterative_reducing_and_clustering_using_hierarchies": "birch",
    ":density_based_spatial_clustering_of_applications_with_noise": "dbscan",
    ":k_means": "kmeans",
    ":k_modes": "kmodes",
    ":mean_shift_clustering": "meanshift",
    ":ordering_points_to_identify_the_clustering_structure": "optics",
    ":spectral_clustering": "sc"
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

    #tabular clustering
    ":metric_pycaret_tabular_clustering": {
                                                    "parameter_name": "optimize",
                                                    "lookup_dict": pycaret_metrics
                                                },

    ":include_approach_pycaret_clustering": {
        "parameter_name": "include_approach",
        "lookup_dict": clustering_approaches,
    },

    ":number_clusters_pycaret_clustering": {
        "parameter_name": "n_clusters",
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
