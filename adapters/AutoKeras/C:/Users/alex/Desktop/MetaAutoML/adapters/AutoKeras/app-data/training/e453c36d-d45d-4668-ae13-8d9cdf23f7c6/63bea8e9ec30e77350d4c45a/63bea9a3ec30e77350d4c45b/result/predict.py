import sys
import json
import dill

import numpy as np
import pandas as pd

import tensorflow as tf
import autokeras as ak
import os
import glob
from PIL import Image
import re

from predict_time_sources import feature_preparation, SplitMethod

def read_image_dataset(json_configuration):

    data_dir = json_configuration["dataset_path"]
    test_df_list =[]

    def read_image_dataset_folder(sub_folder_type):
        files = []
        df = []
        for folder in os.listdir(os.path.join(data_dir, sub_folder_type)):
            files.append(glob.glob(os.path.join(data_dir, sub_folder_type, folder, "*.jp*g")))

        df_list =[]
        for i in range(len(files)):
            df = pd.DataFrame()
            df["name"] = [x for x in files[i]]
            df['outcome'] = i
            df_list.append(df)
        return df_list

    test_df_list = read_image_dataset_folder("test")

    test_data = pd.concat(test_df_list, axis=0,ignore_index=True)

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

    X_test = np.array([img_preprocess(p) for p in test_data.name.values])
    y_test = test_data.outcome.values
    return X_test, y_test

if __name__ == '__main__':
    filepath = sys.argv[1]
    configpath = sys.argv[2]
    save_path = sys.argv[3]
    X = None

    with open(configpath) as file:
        config_json = json.load(file)

    config_json["dataset_configuration"] = json.loads(config_json["dataset_configuration"])
    if config_json["configuration"]["task"] in [":tabular_classification", ":tabular_regression", ":text_classification", ":text_regression", ":time_series"]:
        targets = []
        for key in config_json["dataset_configuration"]["schema"]:
            #Get target columns list
            if config_json["dataset_configuration"]["schema"][key].get("role_selected", "") == ":target":
                targets.append(key)
        target = targets[0]
        delimiters = {
            "comma":        ",",
            "semicolon":    ";",
            "space":        " ",
            "tab":          "\t",
        }

        configuration = {
            "filepath_or_buffer": filepath,
            "delimiter": delimiters[config_json['dataset_configuration']['file_configuration']['delimiter']],
            "skiprows": (config_json['dataset_configuration']['file_configuration']['start_row']-1),
            "decimal": config_json['dataset_configuration']['file_configuration']['decimal_character'],
            "escapechar": config_json['dataset_configuration']['file_configuration']['escape_character'],
            "encoding": config_json['dataset_configuration']['file_configuration']['encoding'],
        }
        if config_json['dataset_configuration']['file_configuration']['thousands_seperator'] != "":
            configuration["thousands"] = config_json['dataset_configuration']['file_configuration']['thousands_seperator']


        X = pd.read_csv(**configuration)
        #Rename untitled columns to correct name
        for column in X:
            if re.match(r"Unnamed: [0-9]+", column):
                X.rename(columns={column: f"Column{X.columns.get_loc(column)}"}, inplace=True)

        X, y = feature_preparation(X, config_json["dataset_configuration"]["schema"].items(), config_json["dataset_configuration"]["file_configuration"]["datetime_format"], is_prediction=True)

    elif config_json["configuration"]["task"] in [":image_classification",  ":image_regression"]:
        X, y = read_image_dataset(config_json)

    with open(sys.path[0] + '/model_keras.p', 'rb') as file:
        loaded_model = dill.load(file)
    if config_json["configuration"]["task"] in [":text_classification", ":text_regression"]:

        predicted_y = loaded_model.predict(np.array(X))
        #predicted_y = [np.round(y[0],0) for y in predicted_y]
    else:
        predicted_y = loaded_model.predict(X)
        #predicted_y = [np.round(y[0],0) for y in predicted_y]

    pd.DataFrame(data=predicted_y, columns=["predicted"]).to_csv(save_path)