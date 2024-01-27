import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from utils import utils

"""
This script is for generating a plot for each task and each automlsolution to plot the size in combination with the best runtime limit for each dataset
"""

file_path = os.path.join(os.getcwd(), "generated_files")
df = pd.read_csv(os.path.join(file_path, "runtimeDataset.csv"))
groups = df.groupby(["task"])
for group in groups:
    automls = group[1].groupby(["AutoML_solution"])
    for automl in automls:
        unique_names = automl[1]["dataset_name"].unique()
        colors = np.random.rand(len(set(unique_names)), 3)
        for i, name in enumerate(unique_names):
            data = automl[1][automl[1]["dataset_name"] == name]
            plt.scatter(data["dataset_size_in_mb"], data["best_runtime_limit"], label=name, color=colors[i])
        utils.plot(automl[1]["AutoML_solution"].unique()[0] + automl[1]["task"].unique()[0],"Size in MB","runtime_limit", "Datasetname" )
