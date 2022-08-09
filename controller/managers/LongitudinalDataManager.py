import pandas as pd
import numpy as np
from typing import Tuple, List
from sktime.datasets import load_from_tsfile_to_dataframe
from sktime.datasets import load_from_tsfile
from sktime.datatypes import convert_to
from Controller_bgrpc import *

FIRST_ROW_AMOUNT = 50
FIRST_N_ITEMS = 3
PD_MULTI_INDEX = "pd-multiindex"
INSTANCES_COL = "instances"
TARGET_COL = "target"


class LongitudinalDataManager:
    """
    Static Longitudinal Data Manager class to interact with the local file system
    """

    @staticmethod
    def read_dataset(path) -> GetDatasetResponse:
        """
        Read the dataset and create it's preview, which will be used on the frontend
        ---
        Parameter
        1. path to the dataset to read
        ---
        Return a GetDatasetResponse containing dataset and it's preview
        """
        response = GetDatasetResponse()
        X, y = load_from_tsfile(path)
        df_x = convert_to(X, to_type=PD_MULTI_INDEX)
        df_y = pd.DataFrame(y, columns=[TARGET_COL])
        # Merge the panel data and labels into a single long format pandas dataset
        dataset = df_x.merge(df_y, left_on=INSTANCES_COL, right_index=True)
        # dataset = load_from_tsfile_to_dataframe(path, return_separate_X_and_y=False)
        # dataset = dataset.rename(columns={"class_vals": TARGET_COL})

        for col in dataset.columns:
            table_column = TableColumn()
            table_column.name = col
            numpy_datatype = dataset[col].dtype.name
            datatype, convertible_types = LongitudinalDataManager.__get_datatype(numpy_datatype, dataset[col])

            table_column.type = datatype
            for convertible_type in convertible_types:
                table_column.convertible_types.append(convertible_type)

            if (col == TARGET_COL):
                # for item in dataset[col].head(FIRST_ROW_AMOUNT).tolist():
                for item in df_y[col].head(FIRST_ROW_AMOUNT).tolist():
                    table_column.first_entries.append(str(item))
            else:
                # for item in dataset[col].head(FIRST_ROW_AMOUNT):
                for item in X[col].head(FIRST_ROW_AMOUNT):
                    # Create a preview of the given longitudinal dataset
                    preview = item.to_list()
                    preview = preview[0:FIRST_N_ITEMS]
                    preview = str(preview)
                    preview = preview.replace("]", ", ...]")
                    table_column.first_entries.append(preview)

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
        Return DATATYPE of the passed value + List of convertible datatypes
        """
        if numpy_datatype == np.dtype(np.object):
            if column.nunique() < column.size / 10:
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
    def read_dimension_names(path) -> GetTabularDatasetColumnResponse:
        """
        Read only the dimension (column) names of the given dataset
        ---
        Parameter
        1. path to the dataset to read
        ---
        Return the column names as GetTabularDatasetColumnNamesResponse
        """
        response = GetTabularDatasetColumnNamesResponse()
        dataset = load_from_tsfile_to_dataframe(path, return_separate_X_and_y=False)
        dataset = dataset.rename(columns={"class_vals": TARGET_COL})

        for col in dataset.columns:
            response.columnNames.append(col)
        return response
