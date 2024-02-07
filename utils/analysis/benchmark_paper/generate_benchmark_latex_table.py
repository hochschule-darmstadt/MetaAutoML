
import openml
openml.config.apikey = 'cfa10e8e9b677cb8f8a1a716a97fde3d'
import warnings
# Suppress all future warnings
warnings.simplefilter(action='ignore', category=Warning)
from decimal import Decimal, ROUND_HALF_UP
#Use this code to generate the benchmark result table content for latex automatically

import numpy as np
import pandas as pd
dataset_ids = [1169, 41147, 1111, 151, 1461, 4135, 41161, 1471, 1053, 40536, 24, 41142, 1489, 4134, 3, 1067, 1049, 470, 29, 15, 1596, 41167, 40923, 41168, 40996, 40685, 1505, 6, 1476, 1478, 1459, 28, 60, 46, 21, 1491, 54, 188, 42, 40496]
task_ids = [189354, 233138, 3945, 219, 14965, 34539, 168338, 9983, 3904, 146607, 24, 168908, 9952, 14966, 3, 3917, 3902, 3561, 29, 15, 7593, 233137, 167121, 168330, 146825, 146212, 9968, 6, 9986, 14970, 14964, 28, 58, 45, 21, 9954, 53, 2079, 41, 125921]
runs = ["4", "0", "150", "77.7k", "40,5k", "22.1k", "10", "97.3k", "19k", "23.4k", "12.6k", "4", "114k", "19k", "174k", "159k", "113k", "13.2k", "21.2k", "24.6k", "5", "0", "43", "12", "451", "10", "10.4k", "35k", "10.7k", "16.7k", "11.7k", "21.7k", "14.8k", "20.6k", "12.6k", "13.7k", "25.3k", "20.2k", "16.1k", "13.1k"]
oma_ml_acc_score = [0.674, 0.680, 0.982, 0.949, 0.911, 0.948, 0.998, 0.980, 0.818, 1.000, 1.000, 0.763, 0.901, 0.795, 0.997, 0.886, 0.928, 0.756, 0.862, 0.964, 0.970, 0.933, 0.967, 0.725, 0.902, 1.000, 1.000, 0.980, 0.996, 0.994, 0.951, 0.990, 0.873, 1.000, 1.000, 0.884, 0.847, 0.703, 0.978, 0.700]
oma_ml_f1_score = [0.645, 0.711, 0.211, 0.939, 0.951, 0.973, 0.996, 0.982, 0.290, 1.000, 1.000, 0.758, 0.931, 0.814, 0.997, 0.544, 0.712, 0.560, 0.877, 0.950, 0.941, 0.931, 0.967, 0.582, 0.901, 0.996, 1.000, 0.979, 0.996, 0.995, 0.947, 0.990, 0.872, 1.000, 1.000, 0.874, 0.845, 0.682, 0.981, 0.698]
oma_ml_auroc_score = [0.727, 0.749, 0.865, 0.987, 0.936, 0.862, 1.000, 0.997, 0.746, 1.000, 1.000, 0.819, 0.956, 0.871, 1.000, 0.842, 0.955, 0.779, 0.921, 0.994, 0.999, 1.000, 0.999, 0.883, 0.993, 1.000, 1.000, 1.000, 1.000, 1.000, 0.997, 1.000, 0.975, 1.000, 1.000, 0.998, 0.963, 0.925, 0.998, 0.944]


def get_values_list_for_evaluation(task_id, metric):
    task = openml.tasks.get_task(task_id)

    evals = openml.evaluations.list_evaluations(size=None,
        function=metric, tasks=[task_id], output_format="dataframe"
    )
    asd = pd.Series()
    df = pd.DataFrame()
    if evals.empty == True:
        return []
    flow_ids = evals.flow_id.unique()
    for i in range(len(flow_ids)):
        flow_values = evals[evals.flow_id == flow_ids[i]].value
        asd = pd.concat([asd, flow_values])
    return asd.tolist()


for i in range(0, 40):
    print(f"& {dataset_ids[i]} & {task_ids[i]} & {runs[i]} & ", end='')
    accs = get_values_list_for_evaluation(task_ids[i], 'predictive_accuracy')
    if accs:
        best_acc = Decimal(max(accs)).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
    else:
        best_acc = "-"
    print(f"{best_acc} & {oma_ml_acc_score[i]} & ", end='')
    
    f1s = get_values_list_for_evaluation(task_ids[i], 'f_measure')
    if f1s:
        best_f1 = Decimal(max(f1s)).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
    else:
        best_f1 = "-"
    print(f"{best_f1} & {oma_ml_f1_score[i]} & ", end='')
    
    aurocs = get_values_list_for_evaluation(task_ids[i], 'f_measure')
    if aurocs:
        best_auroc = Decimal(max(aurocs)).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
    else:
        best_auroc = "-"
    print(f"{best_auroc} & {oma_ml_auroc_score[i]} \\\\")


print()