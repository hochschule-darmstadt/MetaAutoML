import json
import os
import shutil
import subprocess
import sys
import time
#import autokeras as ak
#import tensorflow as tf

import Adapter_pb2
import Adapter_pb2_grpc
import dill
import grpc
import numpy as np
import pandas as pd
from predict_time_sources import DataType, SplitMethod, feature_preparation
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sktime.datatypes import convert_to
from sktime.datasets import load_from_tsfile_to_dataframe

from JsonUtil import get_config_property
from TemplateGenerator import TemplateGenerator
import glob
from PIL import Image

######################################################################
## LONGITUDINAL DATASET HELPER FUNCTIONS
######################################################################

#region


def split_dataset(dataset, json_configuration):
    """
    Split the given dataset into train and test subsets
    """
    split_method = json_configuration["test_configuration"]["method"]
    split_ratio = json_configuration["test_configuration"]["split_ratio"]
    random_state = json_configuration["test_configuration"]["random_state"]
    np.random.seed(random_state)

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


def read_longitudinal_dataset(json_configuration):
    """
    Read longitudinal data from the `.ts` file
    """
    file_path = os.path.join(json_configuration["file_location"], json_configuration["file_name"])
    dataset = load_from_tsfile_to_dataframe(file_path, return_separate_X_and_y=False)
    dataset = dataset.rename(columns={"class_vals": "target"})
    return split_dataset(dataset, json_configuration)


def convert_longitudinal_to_numpy(X, y, one_hot_encoder):
    """
    Convert the panel dataset to numpy3D
    """
    X_np = convert_to(X, to_type="numpy3D")
    y_binary = one_hot_encoder.transform(y.reshape(-1, 1)).toarray()
    return X_np, y_binary

#endregion