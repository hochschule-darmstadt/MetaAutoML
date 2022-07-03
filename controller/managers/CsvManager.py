import pandas as pd
import numpy as np
from Controller_bgrpc import *

from DataSetAnalysisManager import DataSetAnalysisManager

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
        # P: Dataset Analysis happens here, will return small json with metadata
        

        analysisResult = DataSetAnalysisManager.startAnalysis(dataset)
        DataSetAnalysisManager.persistAnalysisResult(analysisResult)
    
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
            if column.nunique() < column.size/10:
                if column.nunique() <= 2:
                    return DataType.DATATYPE_BOOLEAN, [DataType.DATATYPE_IGNORE,
                                                             DataType.DATATYPE_CATEGORY]
                return DataType.DATATYPE_CATEGORY, [DataType.DATATYPE_IGNORE]
            return DataType.DATATYPE_IGNORE, [DataType.DATATYPE_CATEGORY]
        elif numpy_datatype == np.dtype(np.unicode_):
            return DataType.DATATYPE_STRING
        elif numpy_datatype == np.dtype(np.int64):
            if "id" in str.lower(str(column.name)) and column.nunique() == column.size:
                return DataType.DATATYPE_IGNORE, []
            elif column.nunique() <= 2:
                return DataType.DATATYPE_BOOLEAN, [DataType.DATATYPE_IGNORE,
                                                         DataType.DATATYPE_CATEGORY,
                                                         DataType.DATATYPE_INT]
            if column.nunique() < 10:
                return DataType.DATATYPE_CATEGORY, [DataType.DATATYPE_IGNORE,
                                                          DataType.DATATYPE_INT]
            return DataType.DATATYPE_INT, [DataType.DATATYPE_IGNORE,
                                                 DataType.DATATYPE_CATEGORY]
        elif numpy_datatype == np.dtype(np.float_):
            return DataType.DATATYPE_FLOAT, [DataType.DATATYPE_IGNORE,
                                                   DataType.DATATYPE_CATEGORY,
                                                   DataType.DATATYPE_INT]
        elif numpy_datatype == np.dtype(np.bool_):
            return DataType.DATATYPE_BOOLEAN, [DataType.DATATYPE_IGNORE,
                                                     DataType.DATATYPE_CATEGORY,
                                                     DataType.DATATYPE_INT,
                                                     DataType.DATATYPE_FLOAT]
        elif numpy_datatype == np.dtype(np.datetime64):
            return DataType.DATATYPE_DATETIME, [DataType.DATATYPE_IGNORE,
                                                      DataType.DATATYPE_CATEGORY]
        else:
            return DataType.DATATYPE_UNKNOW, [DataType.DATATYPE_IGNORE,
                                                    DataType.DATATYPE_CATEGORY,
                                                    DataType.DATATYPE_BOOLEAN]

    @staticmethod
    def read_column_names(path) -> GetTabularDatasetColumnNamesResponse:
        """
        Read only the column names of a dataset
        ---
        Parameter
        1. path to the dataset to read
        ---
        Return the column names as GetTabularDatasetColumnNamesResponse
        """
        response = GetTabularDatasetColumnNamesResponse()
        dataset = pd.read_csv(path)
        for col in dataset.columns:
            response.columnNames.append(col)
        return response

    @staticmethod
    def ReadDefaultDatasetAsBytes():
        file = open(os.path.join( os.path.dirname( __file__ ), "../config/defaults/titanic_train.csv"))
        data = file.read().encode()
        file.close()
        return data
