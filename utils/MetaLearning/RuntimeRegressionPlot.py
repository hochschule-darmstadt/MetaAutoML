import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import os
from utils import utils

"""
This script is for generating a plot for each task to plot the size in combination with the best runtime limit for each dataset
Also it plots the linear regession for the calculated parameters for the runtime prediction
"""

file_path = os.path.join(os.getcwd(), "generated_files")
df = pd.read_csv(os.path.join(file_path, "runtimeDataset.csv"))
with open(os.path.join(file_path , "runtime_prediction_parameters.json"), "r") as f:
      parameter = json.load(f)
groups = df.groupby(["task"])
for group in groups:
    unique_names = group[1]["AutoML_solution"].unique()
    colors = np.random.rand(len(set(unique_names)), 3)
    task = group[1]["task"].unique()[0]
    for i, name in enumerate(unique_names):
        data = group[1][group[1]["AutoML_solution"] == name]
        plt.scatter(data["dataset_size_in_mb"], data["best_runtime_limit"], label=name, color=colors[i])
    x_data = np.linspace(0, group[1]["dataset_size_in_mb"].max() , 100)
    y_line = [parameter[task]["m"]* x + parameter[task]["b"] for x in x_data]
    plt.plot(x_data, y_line, color = "red")
    utils.plot(task,"Size in MB","runtime_limit", "AutoMLSolution" )
