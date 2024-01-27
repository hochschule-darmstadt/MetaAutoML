import pandas as pd
import utils.utils as utils
import os

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
                    mesaure_string = utils.get_measure(automl[1]["task"].unique(), measure_classification, measure_regression)
                    max_value = sorted[sorted[mesaure_string] < 10000][mesaure_string].max()
                    for index, row in sorted.iterrows():
                        # all values should be between 0 and 10000
                        if row[mesaure_string] > 0 and row[mesaure_string] < 10000:
                            # Checks whether the distance between the value and the next value is less than 1% and also whether the distance to the largest value is less than 5%
                            if abs(utils.divide(row[mesaure_string] - last_measure, last_measure)) < 0.01 and abs(utils.divide(max_value - row[mesaure_string], row[mesaure_string]) < 0.05):
                                new_row = {"dataset_name": row["dataset_name"], "AutoML_solution": row["AutoML_solution"], "dataset_size_in_mb": row["dataset_size_in_mb"],
                                            "best_runtime_limit": last_runtime_limit, mesaure_string: last_measure, "task": automl[1]["task"].unique()}
                                runtime_df = pd.concat([runtime_df, pd.DataFrame([new_row])], ignore_index=True )
                                break
                            last_measure = row[mesaure_string]
                            last_runtime_limit = row["runtime_limit"]

    runtime_df.to_csv(os.path.join(file_path, "runtimeDataset.csv"))



