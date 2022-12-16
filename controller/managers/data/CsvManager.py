import pandas as pd
import numpy as np
from ControllerBGRPC import *
from JsonUtil import get_config_property
import sys

import shutil
import os

FIRST_ROW_AMOUNT = 50


class CsvManager:
    """
    Static CSV Manager class to interact with the local file system
    """


    def read_dataset(path) -> GetDatasetResponse:
        """
        Read a dataset from the disk
        ---
        Parameter
        1. path of the file to read
        ---
        Return a GetDatasetResponse object representing the dataset
        """
        response = GetDatasetResponse()
        dataset = pd.read_csv(path)

        for col in dataset.columns:
            table_column = TableColumn()
            table_column.name = col
            numpy_datatype = dataset[col].dtype.name
            datatype, convertible_types = CsvManager.__get_datatype(numpy_datatype, dataset[col])

            table_column.type = datatype
            for convertible_type in convertible_types:
                table_column.convertible_types.append(convertible_type)

            for item in dataset[col].head(FIRST_ROW_AMOUNT).tolist():
                table_column.first_entries.append(str(item))

            response.columns.append(table_column)

        return response


    @staticmethod
    def __get_datatype(numpy_datatype: np.dtype, column: pd.Series):
        """
        Identify the np datatype and mark correct OMAML datatype
        ---
        Parameter
        1. data type of the current column
        2. current column
        ---
        Return DataType.DATATYPE of the passed value + List of convertible datatypes
        """
        if numpy_datatype == np.dtype(np.object):
            return ":string"
        elif numpy_datatype == np.dtype(np.unicode_):
            return ":string"
        elif numpy_datatype == np.dtype(np.int64):
            if "id" in str.lower(str(column.name)) and column.nunique() == column.size:
                return ":integer"
            elif column.nunique() <= 2:
                return ":boolean"
            return ":integer"
        elif numpy_datatype == np.dtype(np.float_):
            return ":float"
        elif numpy_datatype == np.dtype(np.bool_):
            return ":boolean"
        elif numpy_datatype == np.dtype(np.datetime64):
            return ":datetime"
        else:
            return ":string"

    @staticmethod
    def get_default_column_datatypes_and_roles(path: str, fileConfiguration: dict) -> tuple[dict, dict]:
        """Get the default datatypes of all columns for a CSV based dataset (tabular, text, time series)

		Args:
			path (str): File path to the csv dataset file
			fileConfiguration (dict): The datasets file configuration

		Returns:
			tuple[dict, dict]: Tuple of dictonaries. First dict is the dict of column names and their found default datatype, second dict is the dict of column names and their default roles
		"""
        delimiters = {
            "comma":        ",",
            "semicolon":    ";",
            "space":        " ",
            "tab":          "\t",
        }
        datatypes = {}
        roles = {}
        dataset = pd.read_csv(path, delimiter=delimiters[fileConfiguration['delimiter']], skiprows=(fileConfiguration['start_row']-1), escapechar=fileConfiguration['escape_character'], decimal=fileConfiguration['decimal_character'], encoding=fileConfiguration['encoding'])

        for col in dataset.columns:
            roles.update({col: ":none"})
            numpy_datatype = dataset[col].dtype.name
            datatypes.update({col: CsvManager.__get_datatype(numpy_datatype, dataset[col])})
        return roles, datatypes

    @staticmethod
    def copy_default_dataset(username):
        upload_folder = os.path.join(os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__)), get_config_property("datasets-path"), username, "uploads")
        default_file = os.path.join(os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__)), "config", "defaults", "titanic_train.csv")
        os.makedirs(upload_folder, exist_ok=True)
        shutil.copy(default_file, os.path.join(upload_folder, "titanic_train.csv"))
        return
