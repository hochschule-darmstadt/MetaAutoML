import pandas as pd
from typing import Tuple
from sklearn.preprocessing import OrdinalEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
from _collections_abc import dict_items
from JsonUtil import get_config_property
from AdapterBGRPC import *
import os
import re
import json
import numpy as np

def read_tabular_dataset_training_data(config: "StartAutoMlRequest", perform_splitting: bool) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Read a CSV dataset into train and test dataframes

    Args:
        config (StartAutoMlRequest): The extended training request configuration holding the training paths
        perform_splitting (bool): if the dataset should be divided into 80 /20

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: Dataframes tuple holding the training and test datasets
    """
    delimiters = {
        "comma":        ",",
        "semicolon":    ";",
        "space":        " ",
        "tab":          "\t",
    }

    configuration = {
        "filepath_or_buffer": os.path.join(config["dataset_path"]),
        "delimiter": delimiters[config['dataset_configuration']['file_configuration']['delimiter']],
        "skiprows": (config['dataset_configuration']['file_configuration']['start_row']-1),
        "decimal": config['dataset_configuration']['file_configuration']['decimal_character'],
        "escapechar": config['dataset_configuration']['file_configuration']['escape_character'],
        "encoding": config['dataset_configuration']['file_configuration']['encoding'],
    }
    if config['dataset_configuration']['file_configuration']['thousands_seperator'] != "":
        configuration["thousands"] = config['dataset_configuration']['file_configuration']['thousands_seperator']


    data = pd.read_csv(**configuration)

    if config['dataset_configuration']['multi_fidelity_level'] != 0:
        data = data.sample(frac=0.1, random_state=1)

    #Rename untitled columns to correct name
    for column in data:
        if re.match(r"Unnamed: [0-9]+", column):
            data.rename(columns={column: f"Column{data.columns.get_loc(column)}"}, inplace=True)

    # convert all object columns to categories, because autosklearn only supports numerical,
    # bool and categorical features
    #TODO: change to ontology based preprocessing
    #data[data.select_dtypes(['object']).columns] = data.select_dtypes(['object']).apply(lambda x: x.astype('category'))

    # split training set
    #if SplitMethod.SPLIT_METHOD_RANDOM.value == json_configuration["test_configuration"]["method"]:
    #    train = data.sample(random_state=json_configuration["test_configuration"]["random_state"], frac=1)
    #    test = data.sample(random_state=json_configuration["test_configuration"]["random_state"], frac=1)
    #else:

    if perform_splitting == True:
        train = data.iloc[:int(data.shape[0] * 0.8)]
        test = data.iloc[int(data.shape[0] * 0.8):]
    else:
        train = data
        test = pd.DataFrame()
    return train, test

def write_tabular_dataset_data(df: pd.DataFrame, dir_name: str, config, file_name: str = "test.csv") -> str:
    """Writes dataframe into a csv file.

    Args:
        df (pd.DataFrame): The dataset dataframe
        dir_name (str): path of output directory
        config (dict): the adapter process configuration
        file_name (str): file name

    Returns:
        file_path (str): file path to output file "test.csv"
    """
    delimiters = {
        "comma":        ",",
        "semicolon":    ";",
        "space":        " ",
        "tab":          "\t",
    }

    file_path = os.path.join(dir_name, file_name)
    configuration = {
        "path_or_buf": file_path,
        "sep": delimiters[config["dataset_configuration"]["file_configuration"]['delimiter']],
        "decimal": config["dataset_configuration"]["file_configuration"]['decimal_character'],
        "escapechar": config["dataset_configuration"]["file_configuration"]['escape_character'],
        "encoding": config["dataset_configuration"]["file_configuration"]['encoding'],
        "date_format": config["dataset_configuration"]["file_configuration"]["datetime_format"],
        "index": False
    }

    #np.reshape(df, (-1, 1))
    pd.DataFrame(data=df, columns=df.columns).to_csv(**configuration)
    os.chmod(file_path, 0o744)
    return file_path

def feature_preparation(X: pd.DataFrame, features: dict_items, datetime_format: str, is_prediction:bool=False) -> Tuple[pd.DataFrame, pd.Series]:
    """Prepare the dataset by applying to every column the correct datatype and role

    Args:
        X (pd.DataFrame): The read dataset as a dataframe
        features (dict_items): The dataset schema dictonary as an iterable dict (dict.items())
        datetime_format (str): The string datetime format to use for datetime columns
        is_prediction (bool, optional): Whether or not we are doing a training or prediction run. Defaults to False.

    Returns:
        Tuple[pd.DataFrame, pd.Series]: Tuple of the prepared feature dataframe (X) and label series (y)
    """
    target = ""
    is_target_found = False
    index_columns = []
    for column, dt in features:
        #During the prediction process no target column was read, so unnamed column names will be off by -1 index,
        #if they are located after the target column within the training set, their index must be adjusted
        if re.match(r"Column[0-9]+", column) and is_target_found == True and is_prediction == True:
            column_index = re.findall('[0-9]+', column)
            column_index = int(column_index[0])
            X.rename(columns={f"Column{column_index-1}": column}, inplace=True)

        #Check if column is to be droped, when its role is ignore
        if dt.get("role_selected", "") == ":ignore":
            X.drop(column, axis=1, inplace=True)
            continue
        #Get column datatype
        datatype = dt.get("datatype_selected", "")
        if datatype == "":
            datatype = dt["datatype_detected"]

        #during predicitons we dont have a target column and must avoid casting it
        if dt.get("role_selected", "") == ":target" and is_prediction == True:
            is_target_found = True
            continue

        if datatype == ":categorical":
            X[column] = X[column].astype('category')
        elif datatype == ":boolean":
            X[column] = X[column].astype('bool')
        elif datatype == ":integer":
            X[column] = X[column].astype('int64')
        elif datatype == ":float":
            X[column] = X[column].astype('float64')
        elif datatype == ":datetime":
            X[column] = pd.to_datetime(X[column], format=datetime_format)
        elif datatype == ":string":
            X[column] = X[column].astype('object')

        #Get target column
        if dt.get("role_selected", "") == ":target":
            target = column
            is_target_found = True

        if dt.get("role_selected", "") == ":index":
            index_columns.append(column)

    if len(index_columns) > 0:
        #Set index columns
        X.set_index(index_columns, inplace=True)
    #Handle target column appropriately depending on runtime
    if is_prediction == True:
        y = pd.Series()
    else:
        y = X[target]
        X.drop(target, axis=1, inplace=True)


    return X, y

def set_column_with_largest_amout_of_text(X: pd.DataFrame, configuration: dict) -> dict:
    """
    Find the column with the most text inside,
    because some adapters only supports text training with one feature
    Args:
        X (pd.DataFrame): The current X Dataframe
        configuration (dict): hold the current adapter process configuration

    Returns:
        dict: Returns a the dict is the updated configuraiton dict
    """
    column_names = []
    target = ""
    dict_with_string_length = {}

    #First get only columns that will be used during training
    for column, dt in configuration["dataset_configuration"]["schema"].items():
        if dt.get("role_selected", "") == ":ignore" or dt.get("role_selected", "") == ":index" or dt.get("role_selected", "") == ":target":
            continue
        column_names.append(column)

    #Check the used columns by dtype object (== string type) and get mean len to get column with longest text
    for column_name in column_names:
        if(X.dtypes[column_name] == object):
            newlength = X[column_name].astype(str).str.len().mean()
            dict_with_string_length[column_name] = newlength
    max_value = max(dict_with_string_length, key=dict_with_string_length.get)

    #Remove the to be used text column from the list of used columns and set role ignore as Autokeras can only use one input column for text tasks
    column_names.remove(max_value)
    for column_name in column_names:
        configuration["dataset_configuration"]["schema"][column_name]["role_selected"] = ":ignore"

    save_configuration_in_json(configuration)
    return configuration

def reset_index_role(config, ignore_index=False):
    """reset the index role for index columns

    Args:
        config (_type_): The training configuration

    Returns:
        _type_: the updated training configuration
    """
    for column, dt in config["dataset_configuration"]["schema"].items():
        if dt.get("role_selected", "") == ":index":
            if ignore_index == True:
                config["dataset_configuration"]["schema"][column]["role_selected"] = ":ignore"
            else:
                del config["dataset_configuration"]["schema"][column]["role_selected"]
    save_configuration_in_json(config)
    return config

def set_encoding_for_string_columns(config, X: pd.DataFrame, y: pd.Series, also_categorical=False):
    """Set encoding for string columns to ordinal if 2 or less unique values else one hot encoding

    Args:
        config (_type_): The training configuration
        X (pd.DataFrame): the training data
        also_categorical (bool, optional): If also categorical set columns are adjusted. Defaults to False.

    Returns:
        _type_: the updated training configuration
    """
    X[y.name] = y.values
    for column, dt in config["dataset_configuration"]["schema"].items():
        if (dt.get("role_selected", "") != ":ignore"
        and (dt.get("datatype_selected", "") == ":string" or dt.get("datatype_selected", "") == ":categorical" and also_categorical==True)
        or (dt.get("datatype_detected", "") == ":string" and dt.get("datatype_selected", "") == "" or dt.get("datatype_detected", "") == ":categorical" and dt.get("datatype_selected", "") == "" and also_categorical==True)):
            #Only update columns that are either selected or auto detected as sting and categorial (if also_categorical==True)
            if dt["preprocessing"].get("encoding", "") == "":
                #Only update the preprocessing if no previews ending block exists
                values = X[column].unique().reshape(-1, 1)
                if dt.get("role_selected", "") == ":target":
                    #if column is target we use label encoding
                    encoding = ":label_encoding"
                elif len(values) == len(X[column]):
                    #elif len is equal to column, it means every row has a unique string, ordinal endoding as this is an index value
                    encoding = ":ordinal_encoding"
                elif len(values) > 2:
                    #elif more than two unique values default to one hot encoding
                    encoding = ":one_hot_encoding"
                else:
                    #If 2 or less default to ordinal encoding
                    encoding = ":ordinal_encoding"
                config["dataset_configuration"]["schema"][column]["preprocessing"].update({"encoding": {"type": encoding, "values": values.tolist()}})

    save_configuration_in_json(config)
    return config

def set_imputation_for_numerical_columns(config, X: pd.DataFrame):
    """Set imputation for numerical columns to ordinal if simple imputer

    Args:
        config (_type_): The training configuration
        X (pd.DataFrame): the training data

    Returns:
        _type_: the updated training configuration
    """
    for column, dt in config["dataset_configuration"]["schema"].items():
        if dt.get("role_selected", "") != ":ignore" and dt.get("role_selected", "") != ":target" and dt.get("role_selected", "") != ":index":
            if X[column].isnull().all():
                #If the entire column is nan we cant impute and will set it to ignore
                dt["role_selected"] = ":ignore"
            elif X[column].isnull().values.any():
                #Only update the preprocessing if no previews ending block exists
                if dt["preprocessing"].get("imputation", "") == "":
                    if dt.get("datatype_selected", "") == ":integer" or dt.get("datatype_detected", "") == ":integer" and dt.get("datatype_selected", "") == "":
                        imputation = ":simple_imputer"
                        imp_config = { "strategy": "mean"}
                        config["dataset_configuration"]["schema"][column]["preprocessing"].update({"imputation": {"type": imputation, "configuration": imp_config, "values": X[column].iloc[:25].tolist()}})
                    elif dt.get("datatype_selected", "") == ":float" or dt.get("datatype_detected", "") == ":float" and dt.get("datatype_selected", "") == "":
                        imputation = ":simple_imputer"
                        imp_config = { "strategy": "mean"}
                        config["dataset_configuration"]["schema"][column]["preprocessing"].update({"imputation": {"type": imputation, "configuration": imp_config, "values": X[column].iloc[:25].tolist()}})
                    elif dt.get("datatype_selected", "") == ":boolean" or dt.get("datatype_detected", "") == ":boolean" and dt.get("datatype_selected", "") == "":
                        imputation = ":simple_imputer"
                        imp_config = { "strategy": "most_frequent"}
                        config["dataset_configuration"]["schema"][column]["preprocessing"].update({"imputation": {"type": imputation, "configuration": imp_config, "values": X[column].iloc[:25].tolist()}})

    save_configuration_in_json(config)
    return config

def replace_forbidden_json_utf8_characters(X: pd.DataFrame, y: pd.Series) -> Tuple[pd.DataFrame, pd.Series]:
    """Replace forbidden json UTF8 characters in feature names

    Args:
        X (pd.DataFrame): The feature dataframe (X)
        y (pd.Series): The label series (y)

    Returns:
        Tuple[pd.DataFrame, pd.Series]: Tuple of the prepared feature dataframe (X) and label series (y)
    """
    for column in X.columns:
        new_column_name = column.translate({ 91 : None, 93 : None, 123 : None, 125 : None, 44 : None, 58 : None, 34 : None})
        X.rename(columns = { column : new_column_name}, inplace=True)

    y.rename(y.name.translate({ 91 : None, 93 : None, 123 : None, 125 : None, 44 : None, 58 : None, 34 : None}), inplace=True)
    return X, y

def string_feature_encoding(X: pd.DataFrame, y: pd.Series, features: dict_items) -> Tuple[pd.DataFrame, pd.Series]:
    """Apply string feature encoding (One hot, ordinal, label encoding) by the column preparation configuration

    Args:
        X (pd.DataFrame): The feature dataframe (X)
        y (pd.Series): The label series (y)
        features (dict_items): The dataset schema dictonary as an iterable dict (dict.items())

    Returns:
        Tuple[pd.DataFrame, pd.Series]: Tuple of the prepared feature dataframe (X) and label series (y)
    """
    for column, dt in features:
        if dt.get("preprocessing", "") == "":
            #Check preprocessing block exists, backwards compability
            dt["preprocessing"] = {}
        if dt["preprocessing"].get("encoding", "") == "":
            continue
        elif dt["preprocessing"]["encoding"]["type"] == ":ordinal_encoding":
            ord_enc = OrdinalEncoder(dtype='int64')
            ord_enc.fit(dt["preprocessing"]["encoding"]["values"])
            X[column] = ord_enc.transform(X[[column]])
        elif dt["preprocessing"]["encoding"]["type"] == ":one_hot_encoding":
            try:
                one_hot_enc = OneHotEncoder(dtype='int64', sparse_output=False).set_output(transform="pandas")
                one_hot_enc.fit(dt["preprocessing"]["encoding"]["values"])
                result = one_hot_enc.transform(X[[column]])
            except:
                #some automl use old sklearn versions we need to check for this
                one_hot_enc = OneHotEncoder(dtype='int64', sparse=False)
                one_hot_enc.fit(dt["preprocessing"]["encoding"]["values"])
                result = pd.DataFrame(columns=one_hot_enc.get_feature_names(), data=one_hot_enc.transform(X[[column]]))

            for col in result.columns:
                result = result.rename(columns={ col : col.replace("x0", column)})
            X = pd.concat([X, result], axis=1).drop(columns=[column])
        elif dt["preprocessing"]["encoding"]["type"] == ":label_encoding":
            label_enc = LabelEncoder()
            label_enc.fit(dt["preprocessing"]["encoding"]["values"])
            y = pd.Series(label_enc.transform(y.values), name=y.name)
        else:
            continue
    return X, y

def numerical_feature_imputation(X: pd.DataFrame, features: dict_items) -> Tuple[pd.DataFrame, pd.Series]:
    """Apply numerical feature imputation  by the column preprocessing configuration

    Args:
        X (pd.DataFrame): The feature dataframe (X)
        features (dict_items): The dataset schema dictonary as an iterable dict (dict.items())

    Returns:
        Tuple[pd.DataFrame, pd.Series]: Tuple of the prepared feature dataframe (X) and label series (y)
    """
    for column, dt in features:
        if dt.get("preprocessing", "") == "":
            #Check preprocessing block exists, backwards compability
            dt["preprocessing"] = {}
        if dt["preprocessing"].get("imputation", "") == "":
            continue
        elif dt["preprocessing"]["imputation"]["type"] == ":simple_imputer":
            simp_impu = SimpleImputer(**dt["preprocessing"]["imputation"]["configuration"])
            simp_impu.fit(np.array(dt["preprocessing"]["imputation"]["values"]).reshape(-1, 1))
            X[column] = simp_impu.transform(X[[column]])
    return X

def prepare_tabular_dataset(df: pd.DataFrame, json_configuration: dict, is_prediction:bool=False) -> Tuple[pd.DataFrame, pd.Series]:
    """Prepare tabular dataset, perform feature preparation and data type casting

    Args:
        df (pd.DataFrame): The dataset dataframe
        json_configuration (dict): the training configuration dictonary
        is_prediction (bool): if the label will be processed

    Returns:
        tuple[pd.DataFrame, object]: tuple holding the dataset dataframe without the target column, and a Series or Dataframe holding the Target column(s) tuple[(X_dataframe, y)]
    """
    X, y = feature_preparation(df, json_configuration["dataset_configuration"]["schema"].items(), json_configuration["dataset_configuration"]["file_configuration"]["datetime_format"], is_prediction)
    X, y = string_feature_encoding(X, y, json_configuration["dataset_configuration"]["schema"].items())
    X = numerical_feature_imputation(X, json_configuration["dataset_configuration"]["schema"].items())
    return X, y

def convert_X_and_y_dataframe_to_numpy(X: pd.DataFrame, y: pd.Series) -> Tuple[np.ndarray, np.ndarray]:
    """Convert the X and y dataframes to numpy datatypes and fill up nans

    Args:
        X (pd.DataFrame): The dataset dataframe holding the features without target
        y (pd.Series): The dataset series holding only the target

    Returns:
        tuple[np.ndarray, np.ndarray]: Tuple holding numpy array versions of the dataset, and target variable tuple[dataset, target]
    """
    X = X.to_numpy()
    X = np.nan_to_num(X, 0)
    y = y.to_numpy()
    return X, y

def save_configuration_in_json(configuration: dict):
    """
    serialize dataset_configuration to json string and save the the complete configuration in json file
    to habe the right datatypes available for the evaluation
    Args:
        configuration (dict): The current adapter process configuration
    """
    configuration['dataset_configuration'] = json.dumps(configuration['dataset_configuration'])
    with open(os.path.join(configuration['job_folder_location'], get_config_property("job-file-name")), "w+") as f:
        json.dump(configuration, f)
    configuration["dataset_configuration"] = json.loads(configuration["dataset_configuration"])
