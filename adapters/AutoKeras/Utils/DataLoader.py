import os

import autokeras as ak
import tensorflow as tf
from AdapterUtils import read_tabular_dataset_training_data


def read_image_dataset(json_configuration):
    """Reads image data and creates AutoKeras specific structure/sets
    ---
    Parameter
    1. config: Job config
    ---
    Return image dataset
    """

    local_dir_path = json_configuration["file_location"]

    # Treat file location like URL if it does not exist as dir. URL/Filename need to be specified.
    # Mainly used for testing purposes in the hard coded json for the job
    # Example: app-data/datasets vs https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz

    if not (os.path.exists(os.path.join(local_dir_path, json_configuration["file_name"]))):
        local_file_path = tf.keras.utils.get_file(
            origin=json_configuration["file_location"], 
            fname="image_data", 
            cache_dir=os.path.abspath(os.path.join("app-data")), 
            extract=True
        )

        local_dir_path = os.path.dirname(local_file_path)

    data_dir = os.path.join(local_dir_path, json_configuration["file_name"])
    train_data = None
    test_data = None

    if(json_configuration["test_configuration"]["dataset_structure"] == 1):
        train_data = ak.image_dataset_from_directory(
            data_dir,
            validation_split=json_configuration["test_configuration"]["split_ratio"],
            subset="training",
            seed=123,
            image_size=(json_configuration["test_configuration"]["image_height"], 
                        json_configuration["test_configuration"]["image_width"]),
            batch_size=json_configuration["test_configuration"]["batch_size"],
        )

        test_data = ak.image_dataset_from_directory(
            data_dir,
            validation_split=json_configuration["test_configuration"]["split_ratio"],
            subset="validation",
            seed=123,
            image_size=(json_configuration["test_configuration"]["image_height"], 
                        json_configuration["test_configuration"]["image_width"]),
            batch_size=json_configuration["test_configuration"]["batch_size"],
        )

    else:
        train_data = ak.image_dataset_from_directory(
            os.path.join(data_dir, "train"),
            image_size=(json_configuration["test_configuration"]["image_height"], 
                        json_configuration["test_configuration"]["image_width"]),
            batch_size = json_configuration["test_configuration"]["batch_size"]
        )

        test_data = ak.image_dataset_from_directory(
            os.path.join(data_dir, "test"), 
            shuffle=False,
            image_size=(json_configuration["test_configuration"]["image_height"], 
                        json_configuration["test_configuration"]["image_width"]),
            batch_size=json_configuration["test_configuration"]["batch_size"]
        )

    return train_data, test_data

def data_loader(config):
    """
    Get exception message
    ---
    Parameter
    1. config: Job config
    ---
    Return job type specific dataset
    """

    train_data = None
    test_data = None

    if config["task"] == 1:
        train_data, test_data = read_tabular_dataset_training_data(config)
    elif config["task"] == 2:
        train_data, test_data = read_tabular_dataset_training_data(config)
    elif config["task"] == 3:
        train_data, test_data = None
    elif config["task"] == 4:
        train_data, test_data = read_image_dataset(config)
    elif config["task"] == 5:
        train_data, test_data = read_image_dataset(config)

    return train_data, test_data
