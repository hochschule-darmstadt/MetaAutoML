import json
import os
import dill
import numpy as np
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sktime.datatypes import convert_to
from sktime.datasets import load_from_tsfile_to_dataframe
from sktime.datasets import load_from_tsfile
from AutoMLs.predict_time_sources import SplitMethod

######################################################################
## LONGITUDINAL DATASET HELPER FUNCTIONS
######################################################################

#region


def split_dataset(X, y, json_configuration):
    """
    Split the given dataset into train and test subsets
    """
    split_method = json_configuration["test_configuration"]["method"]
    split_ratio = json_configuration["test_configuration"]["split_ratio"]
    random_state = json_configuration["test_configuration"]["random_state"]
    np.random.seed(random_state)

    if int(SplitMethod.SPLIT_METHOD_RANDOM.value) == split_method:
        return train_test_split(
            X, y,
            train_size=split_ratio,
            random_state=random_state,
            shuffle=True,
            stratify=y
        )
    else:
        return train_test_split(
            X, y,
            train_size=split_ratio,
            shuffle=False,
            stratify=y
        )


def read_longitudinal_dataset(json_configuration):
    """
    Read longitudinal data from the `.ts` file
    """
    file_path = os.path.join(json_configuration["file_location"], json_configuration["file_name"])
    # dataset = load_from_tsfile_to_dataframe(file_path, return_separate_X_and_y=False)
    # dataset = dataset.rename(columns={"class_vals": "target"})
    # return split_dataset(dataset, json_configuration)
    return load_from_tsfile(file_path, return_y=True, return_data_type="numpy3D")


def convert_longitudinal_to_numpy(X, y, one_hot_encoder):
    """
    Convert the panel dataset to numpy3D
    """
    X_np = convert_to(X, to_type="numpy3D")
    y_binary = one_hot_encoder.transform(y.reshape(-1, 1)).toarray()
    return X_np, y_binary


def export_keras_model(model, path, file_name):
    """
    Saves the given keras model
    ---
    Parameter:
    1. keras model
    2. session id
    3. file name
    """
    save_path = os.path.join(path, file_name)
    model.save(save_path)


def export_one_hot_encoder(one_hot_encoder, path, file_name):
    """
    Saves the given instance of the sklearn.preprocessing.OneHotEncoder class
    ---
    Parameter:
    1. instance of sklearn.preprocessing.OneHotEncoder
    2. session id
    3. file name
    """
    with open(os.path.join(path, file_name), 'wb+') as file:
        dill.dump(one_hot_encoder, file)

#endregion