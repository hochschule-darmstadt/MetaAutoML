import pandas as pd
from bson.objectid import ObjectId
import os
import collection


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

def create_row(df: pd.DataFrame, auto_ml_solution: str, task : str, trainings_id: str, dataset_name: str, dataset_size_mb: float, measure: str,
               measure_value : float, dataset_rows: int, dataset_cols: int, runtime: float, runtime_limit : int, failed = 0):
    """ creates a new row with the variables and adds them to dataframe

    Args:
        df (pd.DataFrame): the dataframe the row should be added
        auto_ml_solution (str): str with the automl solution of the row
        task (str): the task of the row
        trainings_id (str): the training id of the row
        dataset_name (str): the name of the used dataset
        dataset_size_mb (float): the size of the dataset
        measure (str): the string with the measure of the row
        measure_value (float): the value of the measure
        dataset_rows (int): the number rows of the dataset
        dataset_cols (int): the number of columns of the dataset
        runtime (float): the runtime from the dataset
        runtime_limit (int): the set runtime limit
        failed (int, optional): set to 1 when failing. Defaults to 0.

    Returns:
        pd.Dataframe: the dataframe with the new row
    """
    new_row = {"AutoML_solution":auto_ml_solution, "task": task , "trainings_id":trainings_id, "dataset_name": dataset_name, "dataset_size_in_mb" : dataset_size_mb, "dataset_rows": dataset_rows,
               measure: measure_value, "dataset_cols": dataset_cols, "runtime": runtime , "runtime_limit": runtime_limit, "failed": failed}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True )
    return df


def readDatabase(trainings: collection ,datasets: collection, models: collection,file_path: str, measure_classification: str, measure_regression: str):
    """reads the important enttries from the database and saves them in a dataframe
        Also caluclates the relative measurement value for the specific task

    Args:
        trainings (collection): the collection with the training information
        datasets (collection): the collection with the dataset information
        models (collection): the collection with the model information
        file_path (str): the path where the dataset is stored
        measure_classification (str): string with the measurement for classification
        measure_regression (str): string with the measurement for regression
    """
    header_row = ["AutoML_solution", "task", "trainings_id", "dataset_name", "dataset_size_mb", measure_classification, measure_regression, "dataset_rows",
                  "dataset_cols", "runtime", "runtime_limit", "failed", "relative_" + measure_classification , "relative_" + measure_regression]
    df = pd.DataFrame(columns = header_row)
    print("Start")
    for training in trainings.find():
        task = training["configuration"]["task"]
        measure = get_measure(task, measure_classification, measure_regression)
        if "runtime_limit" in training["configuration"]:
            runtime_limit = training["configuration"]["runtime_limit"]
            trainings_id = training["_id"]
            dataset = datasets.find({"_id": ObjectId(training["dataset_id"])})

            for data in dataset:
                dataset_size_byte = data["analysis"]["size_bytes"]
                dataset_size_mb = dataset_size_byte / 1000  / 1000
                dataset_rows = data["analysis"]["number_of_rows"]
                dataset_cols = data["analysis"]["number_of_columns"]
                dataset_name = data["name"]

            list_finished_automls = []
            for id in training["model_ids"]:
                model = models.find({"_id": ObjectId(id)})
                for m in model:
                    list_finished_automls.append(m["auto_ml_solution"])
            for auto_ml_solution in training["configuration"]["selected_auto_ml_solutions"]:
                if auto_ml_solution not in list_finished_automls:
                    if task == ":tabular_classification":
                        measure_value = 0
                    if task == ":tabular_regression":
                        measure_value = 9999999
                    df =  create_row(df,auto_ml_solution, task, trainings_id, dataset_name, dataset_size_mb, measure, measure_value, dataset_rows, dataset_cols, 0, runtime_limit,1)

            for id in training["model_ids"]:
                model = models.find({"_id": ObjectId(id)})
                for m in model:
                    start = m["runtime_profile"]["start_time"]
                    end = m["runtime_profile"]["end_time"]
                    runtime = end - start
                    runtime = runtime.total_seconds() / 60
                    # if the meaures are included they are set, else they have the value -1
                    if measure in  m["test_score"]:
                        measure_value = m["test_score"][measure]
                    else:
                        measure_value = -1
                    auto_ml_solution = m["auto_ml_solution"]
                    df = create_row(df,auto_ml_solution, task, trainings_id, dataset_name, dataset_size_mb, measure, measure_value, dataset_rows, dataset_cols, runtime,  runtime_limit)


    # Calulate relative scores
    groups = df.groupby(["trainings_id"])
    for group in groups:
        if group[1]["task"].unique()[0] == ":tabular_classification":
            max_value = group[1][measure_classification].max()

            if max_value >= 0:
                for row in group[1].iterrows():
                    if max_value == 0:
                        relative_value = 0
                    elif row[1][measure_classification] >= 0:
                        relative_value = row[1][measure_classification] / max_value
                    df.loc[row[0],"relative_"+ measure_classification] = relative_value
        elif group[1]["task"].unique()[0] == ":tabular_regression":
            max_value = group[1][measure_regression].min()
            if max_value >= 0:
                for row in group[1].iterrows():
                    if max_value == 0 and row[1][measure_regression] == 0:
                        relative_value = 1
                    elif max_value == 9999999 and row[1][measure_regression] == 9999999:
                        relative_value = 0
                    else:
                        relative_value =  max_value / row[1][measure_regression]
                    df.loc[row[0],"relative_"+ measure_regression] = relative_value

    if not os.path.exists(file_path):
        os.makedirs(file_path)

    df.to_csv(os.path.join(file_path,"datasetData.csv"))





