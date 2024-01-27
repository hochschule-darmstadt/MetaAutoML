import pandas as pd
import matplotlib.pyplot as plt
import utils.utils as utils
import numpy as np
import os
import helping_scripts.AddInformationFormBenchmark as benchmark

"""
This script plots bins for the tasks to look if there is a correclation between the number of features and the measurement of the task

To start this it is important to have the Benchmark file and add it to generated_files
"""


def create_feature_plots(group: pd.DataFrame, feature: str, b1: int, b2: int):
    """generate plots for the searched feature for the group

    Args:
        group (pd.DataFrame): the group with the data
        feature (str): the searched feature
        b1 (int): lower bin size
        b2 (int): upper bin size
    """
    automls = group[1].groupby(["AutoML_solution"])
    unique_names = group[1]["AutoML_solution"].unique()
    colors = np.random.rand(len(set(unique_names)), 3)
    for automl, i in zip(automls, range(0, len(unique_names))):
        if automl[1]["task"].unique()[0] == ":tabular_classification":
            bin1 = automl[1][automl[1][feature] <= b1 ]
            bin2 = automl[1][automl[1][feature] > b1]
            points = [bin1["relative_"+ measure_classification].mean(), bin2["relative_" + measure_classification].mean()]
            bins = [1, 2]
            plt.scatter(bins, points, label=automl[1]["AutoML_solution"].unique()[0], color=colors[i])
            title = "Classification"
        else:
            bin1 = automl[1][automl[1][feature] <= b2 ]
            bin2 = automl[1][automl[1][feature] > b2 ]
            points = [bin1["relative_"+ measure_regression].mean(), bin2["relative_"+ measure_regression].mean()]
            bins = [1, 2]
            plt.scatter(bins, points, label=automl[1]["AutoML_solution"].unique()[0], color=colors[i])
            title = "Regression"
    plt.xticks([1,2], labels=bins)
    utils.plot(title,feature + " bins","mean performance", "AutoML_solution", (1, 1) )


file_path = os.path.join(os.getcwd(), "generated_files")
benchmark.add_benchmark_features(file_path)
measure_classification = ":balanced_accuracy"
measure_regression = ":rooted_mean_squared_error"
df = pd.read_csv(os.path.join(file_path,"dataset_with_benchmark.csv"))
groups = df.groupby(["task"])
for group in groups:
    create_feature_plots(group, "categorical_features", 10, 10)
    create_feature_plots(group, "numerical_features", 200, 40)


