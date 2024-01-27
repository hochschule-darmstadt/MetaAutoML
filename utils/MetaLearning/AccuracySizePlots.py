
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import utils.utils as utils

"""
This script plots for each task and each automl solution the size of the dataset and the measurement of the task to look for correlations in the data
"""

file_path = os.path.join(os.getcwd(), "generated_files")
df = pd.read_csv(os.path.join(file_path,"datasetData.csv"))

#Variables for the regared measures
measure_classification = ":balanced_accuracy"
measure_regression = ":rooted_mean_squared_error"

groups = df.groupby(["task"])
for group in groups:
    automls = group[1].groupby(["AutoML_solution"])
    unique_names = group[1]["dataset_name"].unique()
    colors = np.random.rand(len(set(unique_names)), 3)
    for automl in automls:
        if automl[1]["task"].unique()[0] == ":tabular_classification":
            for i, name in enumerate(unique_names):
                data = automl[1][automl[1]["dataset_name"] == name]
                plt.scatter(data["dataset_size_in_mb"], data["relative_"+ measure_classification], label=name, color=colors[i])
            utils.plot(automl[1]["AutoML_solution"].unique()[0],"Size in MB", "relative balanced accuracy score","Datasetname")
        else:
            for i, name in enumerate(unique_names):
                data = automl[1][automl[1]["dataset_name"] == name]
                plt.scatter(data["dataset_size_in_mb"], data["relative_" + measure_regression], label=name)
            utils.plot(automl[1]["AutoML_solution"].unique()[0],"Size in MB", "relative rmse","Datasetname")
