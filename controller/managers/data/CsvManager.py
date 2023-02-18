import pandas as pd
import numpy as np
from ControllerBGRPC import *
from JsonUtil import get_config_property
import sys

import shutil
import os
import re

FIRST_ROW_AMOUNT = 50


class CsvManager:
    """
    Static CSV Manager class to interact with the local file system
    """

    @staticmethod
    def read_dataset(path: str, file_configuration: dict, schema: dict) -> pd.DataFrame:
        """Read a csv dataset from disk

        Args:
            path (str): disk path to dataset
            file_configuration (dict): dataset file configuration to read the dataset
            schema (dict): dataset column schema

        Returns:
            pd.DataFrame: the read dataset as a DataFrame
        """
        delimiters = {
            "comma":        ",",
            "semicolon":    ";",
            "space":        " ",
            "tab":          "\t",
        }

        configuration = {
            "filepath_or_buffer": path,
            "delimiter": delimiters[file_configuration['delimiter']],
            "skiprows": (file_configuration['start_row']-1),
            "decimal": file_configuration['decimal_character'],
            "escapechar": file_configuration['escape_character'],
            "encoding": file_configuration['encoding'],
        }
        if file_configuration['thousands_seperator'] != "":
           configuration["thousands"] = file_configuration['thousands_seperator']

        dataset = pd.read_csv(**configuration)

        #Rename untitled columns to correct name
        for column in dataset:
            if re.match(r"Unnamed: [0-9]+", column):
                dataset.rename(columns={column: f"Column{dataset.columns.get_loc(column)}"}, inplace=True)

        for key, values in schema.items():
            try:
                if values["datatype_selected"] != ":datetime":
                    continue
            except KeyError:
                if values["datatype_detected"] != ":datetime":
                    continue
            try:
                dataset[key] = pd.to_datetime(dataset[key], format=file_configuration['datetime_format'])
            except:
                print("datetime conversion failed!")#TODO logging
        return dataset


    @staticmethod
    def __get_datatype_for_column(numpy_datatype: np.dtype, column: pd.Series):
        """
        Identify the np datatype and mark correct OMAML datatype
        ---
        Parameter
        1. data type of the current column
        2. current column
        ---
        Return DataType.DATATYPE of the passed value + List of convertible datatypes
        """

        compatible_casting_datatypes = {
			":string": [":string", ":categorical", ":datetime"],
            ":integer": [":integer", ":float", ":categorical", ":string"],
            ":boolean": [":boolean", ":integer", ":categorical", ":string"],
            ":float": [":float", ":integer", ":categorical", ":string"],
            ":datetime": [":datetime", ":categorical", ":string"],
		}

        if numpy_datatype == np.dtype(np.unicode_) or numpy_datatype == np.dtype(np.object):
            #Fallback if something isnt recognized automatically
            try:
                pd.to_numeric(column, downcast="float64")
                return ":float", compatible_casting_datatypes[":float"]
            except:
                try:
                    pd.to_numeric(column, downcast="int64")
                    if column.nunique() <= 2:
                        return ":boolean", compatible_casting_datatypes[":boolean"]
                    else:
                        return ":integer", compatible_casting_datatypes[":integer"]
                except:
                    return ":string", compatible_casting_datatypes[":string"]
        elif numpy_datatype == np.dtype(np.int64):
            if column.nunique() <= 2:
                return ":boolean", compatible_casting_datatypes[":boolean"]
            return ":integer", compatible_casting_datatypes[":integer"]
        elif numpy_datatype == np.dtype(np.float_):
            return ":float", compatible_casting_datatypes[":float"]
        elif numpy_datatype == np.dtype(np.bool_):
            return ":boolean", compatible_casting_datatypes[":boolean"]
        elif numpy_datatype == np.dtype(np.datetime64):
            return ":datetime", compatible_casting_datatypes[":datetime"]
        else:
            return ":string", compatible_casting_datatypes[":string"]

    @staticmethod
    def __get_compatible_roles_for_column(column: pd.Series) -> list[str]:
        """Get the compatible roles for a given series

        Args:
            column (pd.Series): One column from the dataframe

        Returns:
            list[str]: IRIs list of compatible roles
        """
        roles = [":target", ":ignore"]

        if column.nunique() == column.size:
            roles.append(":index")
        return roles

    @staticmethod
    def get_default_dataset_schema(path: str, fileConfiguration: dict) -> tuple[dict, dict]:
        """Get the default datatypes of all columns for a CSV based dataset (tabular, text, time series)

		Args:
			path (str): File path to the csv dataset file
			fileConfiguration (dict): The datasets file configuration

		Returns:
			tuple[dict, dict]: Tuple of dictonaries. First dict is the dict of column names and their found default datatype, second dict is the dict of column names and their default roles
		"""
        schema = {}
        dataset = CsvManager.read_dataset(path, fileConfiguration, schema)
        for col in dataset.columns:
            numpy_datatype = dataset[col].dtype.name
            datatype_detected, datatypes_compatible = CsvManager.__get_datatype_for_column(numpy_datatype, dataset[col])
            roles_compatible = CsvManager.__get_compatible_roles_for_column(dataset[col])
            schema.update({col: {
                "datatype_detected": datatype_detected,
                "datatypes_compatible": datatypes_compatible,
                "roles_compatible": roles_compatible,
                "preprocessing": {}
             }})
        return schema

    @staticmethod
    def copy_default_dataset(username):
        upload_folder = os.path.join(os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__)), get_config_property("datasets-path"), username, "uploads")
        default_file = os.path.join(os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__)), "config", "defaults", "titanic_train.csv")
        os.makedirs(upload_folder, exist_ok=True)
        shutil.copy(default_file, os.path.join(upload_folder, "titanic_train.csv"))
        return
