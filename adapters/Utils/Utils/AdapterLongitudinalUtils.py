
from typing import Any
import os
from sklearn.model_selection import train_test_split
import numpy as np

def read_longitudinal_dataset(json_configuration: dict):
    """Read longitudinal data from the `.ts` file and generate training and test datasets

    Args:
        json_configuration (dict): The training configuration dictionary

    Returns:
        Any: tuple of training and test dataset
    """
    from sktime.datasets import load_from_tsfile_to_dataframe

    file_path = os.path.join(json_configuration["file_location"], json_configuration["file_name"])
    dataset = load_from_tsfile_to_dataframe(file_path, return_separate_X_and_y=False)
    dataset = dataset.rename(columns={"class_vals": "target"})
    return split_dataset(dataset, json_configuration)


def split_dataset(dataset: Any, json_configuration: dict):
    """Split the given dataset into train and test subsets

    Args:
        dataset (Any): The loaded TS dataset
        json_configuration (dict): The training configuration dictionary

    Returns:
        _type_: tuple of training and test dataset
    """

    split_method = json_configuration["test_configuration"]["method"]
    split_ratio = json_configuration["test_configuration"]["split_ratio"]
    random_state = json_configuration["test_configuration"]["random_state"]
    np.random.seed(random_state)
    #TODO DEPRECATED
    if int(SplitMethod.SPLIT_METHOD_RANDOM.value) == split_method:
        return train_test_split(
            dataset,
            train_size=split_ratio,
            random_state=random_state,
            shuffle=True,
            stratify=dataset["target"]
        )
    else:
        return train_test_split(
            dataset,
            train_size=split_ratio,
            shuffle=False,
            stratify=dataset["target"]
        )


def read_parameter(parameters, intersect_parameter, automl_parameter, default=[None]):
    """Checks if the intersected parameter or if the individual parameter is set

    Args:
        parameters (_type_): all parameters from the config
        intersect_parameter (_type_): common parameter name (broader id)
        automl_parameter (_type_): individual parameter for the automl
        default (list, optional): Default value if none of the above is set. Defaults to [None].

    Returns:
        _type_: Returns all parameter values that are selected (intersected + individual), if none the default value is taken
    """
    value = list()
    try:
        value = parameters[intersect_parameter]['values']
    except:
        pass
    try:
        values2 = parameters[automl_parameter]['values']
        for para in values2:
            if para not in value:
                value.append(para)
    except:
        pass
    if len(value) == 0:
        return default
    else:
        return value

