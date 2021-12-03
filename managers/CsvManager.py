import pandas as pd
import numpy as np
from typing import List

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
            table_column.type = CsvManager.__get_datatype(numpy_datatype)

            for type in CsvManager.__get_convertible_types(numpy_datatype):
                table_column.convertibleTypes.append(type)

            for item in dataset[col].head(FIRST_ROW_AMOUNT).tolist():
                table_column.firstEntries.append(str(item))

            response.columns.append(table_column)

        return response

    @staticmethod
    def __get_datatype(numpy_datatype) -> Controller_pb2.DataType:
        """
        Identify the np datatype and mark correct OMAML datatype
        ---
        Parameter
        1. data type of the current column
        ---
        Return Controller_pb2.DATATYPE of the passed value
        """
        if numpy_datatype == np.dtype(np.object):
            return Controller_pb2.DATATYPE_UNKNOW
        elif numpy_datatype == np.dtype(np.unicode_):
            return Controller_pb2.DATATYPE_STRING
        elif numpy_datatype == np.dtype(np.int64):
            return Controller_pb2.DATATYPE_INT
        elif numpy_datatype == np.dtype(np.float_):
            return Controller_pb2.DATATYPE_FLOAT
        elif numpy_datatype == np.dtype(np.bool_):
            return Controller_pb2.DATATYPE_BOOLEAN
        elif numpy_datatype == np.dtype(np.datetime64):
            return Controller_pb2.DATATYPE_DATETIME
        else:
            return Controller_pb2.DATATYPE_UNKNOW

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

    @staticmethod
    def __get_convertible_types(pandas_datatype: np.dtype) -> list:
        """
        figures out all types that a column can be converted to.
        We keep a simple placeholder algorithm here.
        However, later this might be enhanced to querying the ontology, using a more sophisticated algorithm or using some imported 3rd party module.
        """
        basic_conversions = [Controller_pb2.DATATYPE_UNKNOW, Controller_pb2.DATATYPE_IGNORE, Controller_pb2.DATATYPE_STRING]

        if pandas_datatype == np.dtype(np.int64):
            return basic_conversions + [Controller_pb2.DATATYPE_FLOAT]
        if pandas_datatype == np.dtype(np.bool_):
            return basic_conversions + [Controller_pb2.DATATYPE_CATEGORY, Controller_pb2.DATATYPE_INT, Controller_pb2.DATATYPE_FLOAT]
        else:
            return basic_conversions
