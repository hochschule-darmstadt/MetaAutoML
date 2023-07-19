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

parameters = {
    #tabular classification
    ":metric_tpot_tabular_classification": {
                                                    "parameter_name": "scoring",
                                                    "lookup_dict": tpot_metrics
                                                },
    #tabular regression
    ":metric_tpot_tabular_regression": {
                                                    "parameter_name": "scoring",
                                                    "lookup_dict": tpot_metrics
                                                },
    #image classification
    ":metric_tpot_image_classification": {
                                                    "parameter_name": "scoring",
                                                    "lookup_dict": tpot_metrics
                                                }
}
