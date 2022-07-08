import pandas as pd
import numpy as np
from typing import Tuple, List
from sktime.datasets import load_from_tsfile_to_dataframe
from Controller_bgrpc import *

FIRST_ROW_AMOUNT = 50
FIRST_N_ITEMS = 3
TARGET_COL = "target"

class PanelDataManager:
    """
    Static Panel Data Manager class to interact with the local file system
    """
    @staticmethod
    def read_dataset(path) -> GetDatasetResponse:
        """
        Read the dataset and create it's preview, which will be used on the frontend
        ---
        Parameter
        1. path to the dataset to read
        ---
        Return a Controller_pb2.GetDatasetResponse containing dataset and it's preview
        """
        response = Controller_pb2.GetDatasetResponse()
        dataset = load_from_tsfile_to_dataframe(path, return_separate_X_and_y=False)
        dataset = dataset.rename(columns={"class_vals": TARGET_COL})

        for col in dataset.columns:
            table_column = Controller_pb2.TableColumn()
            table_column.name = col
            numpy_datatype = dataset[col].dtype.name
            datatype, convertible_types = PanelDataManager.__get_datatype(numpy_datatype, dataset[col])

            table_column.type = datatype
            for convertible_type in convertible_types:
                table_column.convertibleTypes.append(convertible_type)

            if (col == TARGET_COL):
                for item in dataset[col].head(FIRST_ROW_AMOUNT).tolist():
                    table_column.firstEntries.append(str(item))
            else:
                for item in dataset[col].head(FIRST_ROW_AMOUNT):
                    # Create a preview of the given panel dataset
                    preview = item.to_list()
                    preview = preview[0:FIRST_N_ITEMS]
                    preview = str(preview)
                    preview = preview.replace("]", ", ...]")
                    table_column.firstEntries.append(preview)

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
        Return Controller_pb2.DATATYPE of the passed value + List of convertible datatypes
        """
        if numpy_datatype == np.dtype(np.object):
            if column.nunique() < column.size/10:
                if column.nunique() <= 2:
                    return Controller_pb2.DATATYPE_BOOLEAN, [Controller_pb2.DATATYPE_IGNORE,
                                                             Controller_pb2.DATATYPE_CATEGORY]
                return Controller_pb2.DATATYPE_CATEGORY, [Controller_pb2.DATATYPE_IGNORE]
            return Controller_pb2.DATATYPE_IGNORE, [Controller_pb2.DATATYPE_CATEGORY]
        elif numpy_datatype == np.dtype(np.unicode_):
            return Controller_pb2.DATATYPE_STRING
        elif numpy_datatype == np.dtype(np.int64):
            if "id" in str.lower(str(column.name)) and column.nunique() == column.size:
                return Controller_pb2.DATATYPE_IGNORE, []
            elif column.nunique() <= 2:
                return Controller_pb2.DATATYPE_BOOLEAN, [Controller_pb2.DATATYPE_IGNORE,
                                                         Controller_pb2.DATATYPE_CATEGORY,
                                                         Controller_pb2.DATATYPE_INT]
            if column.nunique() < 10:
                return Controller_pb2.DATATYPE_CATEGORY, [Controller_pb2.DATATYPE_IGNORE,
                                                          Controller_pb2.DATATYPE_INT]
            return Controller_pb2.DATATYPE_INT, [Controller_pb2.DATATYPE_IGNORE,
                                                 Controller_pb2.DATATYPE_CATEGORY]
        elif numpy_datatype == np.dtype(np.float_):
            return Controller_pb2.DATATYPE_FLOAT, [Controller_pb2.DATATYPE_IGNORE,
                                                   Controller_pb2.DATATYPE_CATEGORY,
                                                   Controller_pb2.DATATYPE_INT]
        elif numpy_datatype == np.dtype(np.bool_):
            return Controller_pb2.DATATYPE_BOOLEAN, [Controller_pb2.DATATYPE_IGNORE,
                                                     Controller_pb2.DATATYPE_CATEGORY,
                                                     Controller_pb2.DATATYPE_INT,
                                                     Controller_pb2.DATATYPE_FLOAT]
        elif numpy_datatype == np.dtype(np.datetime64):
            return Controller_pb2.DATATYPE_DATETIME, [Controller_pb2.DATATYPE_IGNORE,
                                                      Controller_pb2.DATATYPE_CATEGORY]
        else:
            return Controller_pb2.DATATYPE_UNKNOW, [Controller_pb2.DATATYPE_IGNORE,
                                                    Controller_pb2.DATATYPE_CATEGORY,
                                                    Controller_pb2.DATATYPE_BOOLEAN]

    @staticmethod
    def read_dimension_names(path) -> GetTabularDatasetColumnNamesResponse:
        """
        Read only the dimension (column) names of the given dataset
        ---
        Parameter
        1. path to the dataset to read
        ---
        Return the column names as Controller_pb2.GetTabularDatasetColumnNamesResponse
        """
        response = GetTabularDatasetColumnNamesResponse()
        dataset = load_from_tsfile_to_dataframe(path, return_separate_X_and_y=False)
        dataset = dataset.rename(columns={"class_vals": TARGET_COL})

        for col in dataset.columns:
            response.dimensionNames.append(col)
        return response
