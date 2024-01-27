import pandas as pd
import json
import os

def calculate_parameter(dataframe: pd.DataFrame):
    """Calculates the parameter m in the formula y = m*x + b by using the runtime_limit as y and the dataset size as x values.

    Args:
        dataframe (pd.DataFrame): The dataframe with the training data for the calculation

    Returns:
        float: The parameter m
    """
    x_train = dataframe["dataset_size_in_mb"].to_numpy()
    y_train = dataframe["best_runtime_limit"].to_numpy()
    x_mean = sum(x_train) / len(x_train)
    y_mean = sum(y_train) / len(y_train)

    # Calculation of m
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_train, y_train))
    denominator = sum((x - x_mean) ** 2 for x in x_train)
    return numerator / denominator


def calculate_new_parameters(file_path: str):
    """Reads the dataframe and calculate the parameter m
        Then saves the parameter and the intercept b for each task in one file

    Args:
        file_path (str): the path where the dataset is stored
        measure_classification (str): string with the measurement for classification
        measure_regression (str): string with the measurement for regression
    """
    df = pd.read_csv(os.path.join(file_path, "runtimeDataset.csv"))
    groups = df.groupby(["task"])
    b = 5
    parameter = {}
    for group in groups:
        m = calculate_parameter(group[1])
        parameter[group[1]["task"].unique()[0]] = {}
        parameter[group[1]["task"].unique()[0]]["m"] = m
        parameter[group[1]["task"].unique()[0]]["b"] = b


    print(parameter)
    with open(os.path.join(file_path,  "runtime_prediction_parameters.json"), "w") as f:
        json.dump(parameter,f)

