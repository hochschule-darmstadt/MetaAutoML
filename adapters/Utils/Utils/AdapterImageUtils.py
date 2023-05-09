
import glob
from PIL import Image
import pandas as pd
from typing import Tuple
from AdapterBGRPC import *
import numpy as np
import os
import random


def read_image_dataset(config: "StartAutoMlRequest", image_test_folder=False, as_dataframe=False) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Read image dataset and create training and test dataframes

    Args:
        config (StartAutoMlRequest): The extended training request configuration holding the training paths

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: Dataframe tuples holding the different datasets: tuple[(X_train), (y_train)]
    """
    # Treat file location like URL if it does not exist as dir. URL/Filename need to be specified.
    # Mainly used for testing purposes in the hard coded json for the job
    # Example: app-data/datasets vs https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz
    """
    if not (os.path.exists(os.path.join(local_dir_path, json_configuration["file_name"]))):
        local_file_path = tf.keras.utils.get_file(
            origin=json_configuration["file_location"],
            fname="image_data",
            cache_dir=os.path.abspath(os.path.join("app-data")),
            extract=True
        )

        local_dir_path = os.path.dirname(local_file_path)
    """

    #we need to access the train sub folder for training
    data_dir = config["dataset_path"]
    if image_test_folder == True:
        data_dir = os.path.join(data_dir, "test")
    else:
        data_dir = os.path.join(data_dir, "train")
    train_df_list =[]

    if as_dataframe == True:
        root = os.path.abspath(os.path.expanduser(data_dir))
        synsets = []
        exts=('.jpg', '.jpeg', '.png')
        items = {'image': [], 'label': []}
        for folder in sorted(os.listdir(root)):
            path = os.path.join(root, folder)
            if not os.path.isdir(path):
                continue
            label = len(synsets)
            synsets.append(folder)
            for filename in sorted(os.listdir(path)):
                filename = os.path.join(path, filename)
                ext = os.path.splitext(filename)[1]
                if ext.lower() not in exts:
                    continue
                items['image'].append(filename)
                items['label'].append(label)
            df = pd.DataFrame(items)
            y_train = df["label"]
            X_train = df.drop("label", axis=1)
    else:
        def read_image_dataset_folder():
            files = []
            df = []
            for folder in os.listdir(os.path.join(data_dir)):
                files.append(glob.glob(os.path.join(data_dir, folder, "*.jp*g")))

            df_list =[]

            if config['dataset_configuration']['multi_fidelity_level'] != 0:
                df_list = random.choices(df_list, k=int(len(files)*0.1))

            for i in range(len(files)):
                df = pd.DataFrame()
                df["name"] = [x for x in files[i]]
                df['outcome'] = i
                df_list.append(df)
            return df_list

        train_df_list = read_image_dataset_folder()

        train_data = pd.concat(train_df_list, axis=0,ignore_index=True)

        def img_preprocess(img):
            """
            Opens the image and does some preprocessing
            such as converting to RGB, resize and converting to array
            """
            img = Image.open(img)
            img = img.convert('RGB')
            img = img.resize((256,256))
            img = np.asarray(img)/255
            return img

        X_train = np.array([img_preprocess(p) for p in train_data.name.values])
        y_train = train_data.outcome.values
    return X_train, y_train
