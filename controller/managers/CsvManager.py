import pandas as pd
import numpy as np
from typing import Tuple, List

import Controller_pb2

FIRST_ROW_AMOUNT = 50


class CsvManager:
    """
    Static CSV Manager class to interact with the local file system
    """

    @staticmethod
    def read_dataset(path) -> Controller_pb2.GetDatasetResponse:
        """
        Read a dataset from the disk
        ---
        Parameter
        1. path of the file to read
        ---
        Return a Controller_pb2.GetDatasetResponse object representing the dataset
        """
        response = Controller_pb2.GetDatasetResponse()
        dataset = pd.read_csv(path)

        for col in dataset.columns:
            table_column = Controller_pb2.TableColumn()
            table_column.name = col
            numpy_datatype = dataset[col].dtype.name
            datatype, convertible_types = CsvManager.__get_datatype(numpy_datatype, dataset[col])

            table_column.type = datatype
            for convertible_type in convertible_types:
                table_column.convertibleTypes.append(convertible_type)

            for item in dataset[col].head(FIRST_ROW_AMOUNT).tolist():
                table_column.firstEntries.append(str(item))

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
    def read_column_names(path) -> Controller_pb2.GetTabularDatasetColumnNamesResponse:
        """
        Read only the column names of a dataset
        ---
        Parameter
        1. path to the dataset to read
        ---
        Return the column names as Controller_pb2.GetTabularDatasetColumnNamesResponse
        """
        response = Controller_pb2.GetTabularDatasetColumnNamesResponse()
        dataset = pd.read_csv(path)
        for col in dataset.columns:
            response.columnNames.append(col)
        return response
