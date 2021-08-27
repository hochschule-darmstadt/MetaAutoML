import pandas as pd
import numpy as np

import Controller_pb2
import Controller_pb2_grpc

FIRST_ROW_AMOUNT = 50

class CsvManager:
    """
    Static CSV Manager class to interact with the local file system
    """
    @staticmethod
    def ReadDataset(path) -> Controller_pb2.GetDatasetResponse:
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
            column_information = Controller_pb2.TableColumn()
            column_information.name = col
            print(np.dtype(np.int64).type)
            print(np.dtype(np.int64))
            column_information.type = CsvManager.__GetDatatype(dataset[col].dtype)
            for item in dataset[col].head(FIRST_ROW_AMOUNT).tolist():
                column_information.fistEntries.append(str(item))
            response.columns.append(column_information)
        return response

    @staticmethod
    def __GetDatatype(value):
        """
        Identify the np datatype and mark correct OMAML datatype
        ---
        Parameter
        1. data type of the current column
        ---
        Return Controller_pb2.DATATYPE of the passed value
        """
        if value.name == np.dtype(np.object):
            return Controller_pb2.DATATYPE_UNKNOW
        elif value.name == np.dtype(np.unicode_):
            return Controller_pb2.DATATYPE_STRING
        elif value.name == np.dtype(np.int64):
            return Controller_pb2.DATATYPE_INT
        elif value.name == np.dtype(np.float_):
            return Controller_pb2.DATATYPE_FLOAT
        elif value.name == np.dtype(np.bool_):
            return Controller_pb2.DATATYPE_BOOLEAN
        elif value.name == np.dtype(np.datetime64):
            return Controller_pb2.DATATYPE_DATETIME
        else:
            return Controller_pb2.DATATYPE_UNKNOW

    @staticmethod
    def ReadColumnNames(path) -> Controller_pb2.GetTabularDatasetColumnNamesResponse:
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