import pandas as pd
import os

def get_measure(task: str, measure_classification: str, measure_regression: str):
    """look for the task and return the str with the measurement

    Args:
        task (str): the task
        measure_classification (str): the string of the classification measurement
        measure_regression (str): the string of the regression measurement

    Returns:
        str: the str of the measurement for the task
    """
    if task == ":tabular_classification":
        return measure_classification
    if task == ":tabular_regression":
        return measure_regression


def divide(n: float, d: float):
    """ devide n and d and returns 0 if the d is 0
    Args:
        n (float): the nominator
        d (float): the devidator

    Returns:
        float: the value of the dividation
    """
    if d == 0:
        return 0
    else:
        return n / d

def caluclate_runtime_convergenz(file_path: str, measure_classification: str, measure_regression: str):
    """calculates the best runtime limit for each dataset and each automl solution by comparing the prediction measure from each runtime_limit
        if the difference of the measure is under 1 % or the maximum value of the measure is lower than 5 % the runtime_limit is saved as the best
        For the comparision only datasets that have more than 4 different runtime limits are used
    Args:
        file_path (str): the path where the dataset is stored
        measure_classification (str): string with the measurement for classification
        measure_regression (str): string with the measurement for regression
    """

    df = pd.read_csv(os.path.join(file_path ,"datasetData.csv"))

    filtered_groups = []


    groups = df.groupby(["dataset_name"])
    for name, group in groups:
        runtime_set = group["runtime_limit"].unique()
        if {3, 6, 12, 24, 48, 60, 240}.issubset(set(runtime_set)):
            filtered_groups.append(group)

    df = pd.concat(filtered_groups)
    dataset_groups = df.groupby(["dataset_name"])

    runtime_df = pd.DataFrame()

    for dataset in dataset_groups:
        for task in dataset[1].groupby(["task"]):
            for automl in task[1].groupby(["AutoML_solution"]):
                if len(automl[1]["runtime_limit"].unique()) > 4:
                    sorted = automl[1].sort_values(by="runtime_limit", ascending=True)
                    #set to -1 in case they values are all 0
                    last_measure = -1
                    last_runtime_limit = 0
                    mesaure_string = get_measure(automl[1]["task"].unique(), measure_classification, measure_regression)
                    if automl[1]["task"].unique() == ":tabular_classification":
                        max_value = sorted[mesaure_string].max()
                    else:
                        max_value = sorted[sorted[mesaure_string] >= 0][mesaure_string].min()
                    for index, row in sorted.iterrows():
                        # all values should be between 0 and 9999999
                        if row[mesaure_string] > 0 and row[mesaure_string] < 9999999:
                            # Checks whether the distance between the value and the next value is less than 1% and also whether the distance to the largest value is less than 5%
                            if abs(divide(row[mesaure_string] - last_measure, last_measure)) < 0.01 and abs(divide(max_value - row[mesaure_string], row[mesaure_string]) < 0.05):
                                new_row = {"dataset_name": row["dataset_name"], "AutoML_solution": row["AutoML_solution"], "dataset_size_in_mb": row["dataset_size_in_mb"],
                                            "best_runtime_limit": last_runtime_limit, mesaure_string: last_measure, "task": automl[1]["task"].unique(),
                                            "dataset_rows": row["dataset_rows"], "dataset_cols": row["dataset_cols"], "missing_values": row["missing_values"], "duplicated_rows": row["duplicated_rows"], "duplicated_cols": row["duplicated_cols"], "outliers": row["outliers"],}
                                runtime_df = pd.concat([runtime_df, pd.DataFrame([new_row])], ignore_index=True )
                                break
                            last_measure = row[mesaure_string]
                            last_runtime_limit = row["runtime_limit"]

    runtime_df.to_csv(os.path.join(file_path, "runtimeDataset.csv"))
