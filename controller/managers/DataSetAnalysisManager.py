from typing import Dict
import pandas as pd
import numpy as np
import json

class DataSetAnalysisManager:
    """
    Static DataSetAnalysisManager class to analyze the dataset
    """
    
    def startAnalysis(dataset: pd.DataFrame) -> dict:
        """
        Initialization of the analysis, results are written to JSON file
        ---
        Parameter
        1. dataset to be analyzed
        ---
        Return a python dictionary containing dataset analysis
        """
        #Already a dataframe???
        #dataset = pd.read_csv(dataset, delimiter=',')

        jsonfile = {}
        jsonfile["basic analysis"] = {

            "number_of_columns": DataSetAnalysisManager.__number_of_columns(dataset),
            "number_of_rows": DataSetAnalysisManager.__number_of_rows(dataset),
            "na_columns": DataSetAnalysisManager.__missing_values_columns(dataset),
            "high_na_rows": DataSetAnalysisManager.__missing_values_rows(dataset),
            "outlier": DataSetAnalysisManager.__detect_outliers(dataset),
            "duplicate_columns": DataSetAnalysisManager.__detect_duplicate_columns(dataset),
            "duplicate_rows": DataSetAnalysisManager.__detect_duplicate_rows(dataset),
        }

        return jsonfile

    def startLongitudinalDataAnalysis(dataset: pd.DataFrame) -> dict:
        jsonfile = {}
        rows, cols = dataset.shape

        jsonfile["basic analysis"] = {
            "number_of_columns": cols,
            "number_of_rows": rows,
            "na_columns": {},
            "high_na_rows": [],
            "outlier": [],
            "duplicate_columns": [],
            "duplicate_rows": [],
        }
        return jsonfile

    @staticmethod
    def __number_of_columns(dataset: pd.DataFrame) -> int:
        """
        Counts the number of columns in the dataset and adds that information to a JSON file
        ---
        Parameter
        1. dataset to be analyzed
        ---
        Return the number of columns in the dataset
        """
        number_of_columns = dataset.shape[1]
        
        return number_of_columns

    @staticmethod
    def __number_of_rows(dataset: pd.DataFrame) -> int:
        """
        Counts the number of rows in the dataset and adds that information to a JSON file
        ---
        Parameter
        1. dataset to be analyzed
        ---
        Return the number of rows in the dataset
        """
        number_of_rows = dataset.shape[0]

        return number_of_rows

    @staticmethod
    def __missing_values_columns(dataset: pd.DataFrame) -> dict:
        """
        Counts missing values of each column and row and adds that information to a JSON file
        ---
        Parameter
        1. dataset to be analyzed
        ---
        Return a dictionary containing information about the missing values in each column
        """
        # map all columns with the number of missing values
        na_counts = dict(dataset.isna().sum().items())
        
        return na_counts

    @staticmethod
    def __missing_values_rows(dataset: pd.DataFrame) -> 'list[int]':
        """
        Counts missing values of each row and adds the indices of rows with a lot of missing values to a list
        ---
        Parameter
        1. dataset to be analyzed
        ---
        Return a list of indices of rows containing a lot of missing values
        """
        dataset_missings_rows = dataset.isna().sum(axis=1)

        missing_rows_indices = []

        number_of_columns = len(dataset.columns)

        for index, _ in dataset_missings_rows[dataset_missings_rows > (number_of_columns * 0.5)].items():

            missing_rows_indices.append(index)
        
        return missing_rows_indices

    @staticmethod
    def __detect_outliers(dataset: pd.DataFrame) -> 'list[dict]':
        """
        Detects outliers in all columns in a dataset containing floats
        ---
        Parameter
        1. dataset to be analyzed
        ---
        Return a list containing information about outliers on every column of the dataset
        """

        outlier_columns = []

        dataset_numerics_only = dataset.select_dtypes(include=[np.float])   
    
        for column_name in dataset_numerics_only:
            
            current_column = dataset_numerics_only[column_name].copy()
            current_column = current_column.dropna()

            current_column_sorted = current_column.sort_values()

            Q1, Q3 = np.percentile(current_column_sorted, [25,75])
            
            interquartile_range = Q3 - Q1

            lower_boundary = Q1 - 2 * interquartile_range
            upper_boundary = Q3 + 2 * interquartile_range

            current_column_outlier = (current_column < lower_boundary) | (current_column > upper_boundary)

            outlier_indices = current_column_outlier[current_column_outlier].index.values.tolist()

            outlier_indices = [index + 1 for index in outlier_indices]

            outlier_columns.append({column_name: outlier_indices})
        
        return outlier_columns

    @staticmethod
    def __detect_duplicate_columns(dataset: pd.DataFrame) -> 'list[tuple]':
        """
        Detects duplicate columns in a dataset
        ---
        Parameter
        1. dataset to be analyzed
        ---
        Return a list of tuples each containing a pair of duplicate column indices.
        """
        duplicate_column_list = []

        for x in range(dataset.shape[1]):
            col = dataset.iloc[:, x]
            
            for y in range(x + 1, dataset.shape[1]):

                other_col = dataset.iloc[:, y]
                
                if col.equals(other_col):
                    duplicate_column_pair = (x,y)
                    duplicate_column_list.append(duplicate_column_pair)

        return duplicate_column_list

    @staticmethod
    def __detect_duplicate_rows(dataset: pd.DataFrame) -> 'list[tuple]':
        """
        Detects duplicate rows
        ---
        Parameter
        1. dataset to be analyzed
        ---
        Return a list of tuples each containing a pair of duplicate row indices
        """
        duplicate_row_list = []

        # create index column so that rows can later be identified by id
        dataset["index"] = dataset.index

        column_names= list(dataset.columns)
        column_names.remove("index")

        # dataframe containing duplicate rows only
        duplicates_only = dataset[dataset.duplicated(subset=column_names, keep=False)]

        # save the pairs of duplicate rows in a list
        for x in range(duplicates_only.shape[0]):

            row = duplicates_only.iloc[x]
            row_without_index = duplicates_only.iloc[x, :-1]

            for y in range(x + 1, duplicates_only.shape[0]):

                other_row = duplicates_only.iloc[y]
                other_row_without_index = duplicates_only.iloc[y, :-1]

                if row_without_index.equals(other_row_without_index):
                    index1 = row["index"]
                    index2 = other_row["index"]
                    duplicate_row_pair = (int(index1), int(index2))
                    duplicate_row_list.append(duplicate_row_pair)

        return duplicate_row_list
