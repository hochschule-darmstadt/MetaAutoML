import pandas as pd
import os

def check_exisiting(variable: object, else_value: object):
    """check if the value exits or return the else value

    Args:
        variable (object): str or float the variable to check
        else_value (object): str or float the value returned when there is no value

    Returns:
        object: str or float that should be in the column
    """
    if variable.values.size > 0 :
        variable = variable.values[0]
    else:
        variable = else_value
    return variable


def add_benchmark_features(file_path: str):
    """ read values from the benchmark and adds them to the dataset

    Args:
        file_path (str): the path where the dataset is stored

    """
    df = pd.read_csv(os.path.join(file_path ,"datasetData.csv"))
    benchmark = pd.read_excel(os.path.join(file_path ,"OMA-ML_Benchmark.xlsx"), header=3)

    def berechne_neue_spalten(row):
        dataset_name = row["dataset_name"]
        missing_values =  int(check_exisiting(benchmark[benchmark["Dataset"] == dataset_name.split(".")[0]]["Missing values"], -1))
        categorical_features = int(check_exisiting(benchmark[benchmark["Dataset"] == dataset_name.split(".")[0]]["Categorical features"], -1))
        numerical_features = int(check_exisiting(benchmark[benchmark["Dataset"] == dataset_name.split(".")[0]]["Numeric features"], -1))
        type = check_exisiting(benchmark[benchmark["Dataset"] == dataset_name.split(".")[0]]["Task"], "not available")
        return missing_values, categorical_features, numerical_features, type

    df[["missing_values", "categorical_features", "numerical_features", "type"]] = df.apply(berechne_neue_spalten, axis=1, result_type="expand")
    df.to_csv(os.path.join(file_path, "dataset_with_benchmark.csv"))


