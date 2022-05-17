from typing import Dict
import pandas as pd
import numpy as np
import json
from collections import defaultdict

class DataSetAnalysisManager:
    """
    Static DataSetAnalysisManager class to analyze the dataset
    """
    
    def startAnalysis(dataset: pd.DataFrame):
        """
        Initialization of the analysis, results are written to JSON file
        ---
        Parameter
        1. dataset to be analyzed
        ---
        Return None
        """
        jsonfile = defaultdict(dict)
        jsonfile = DataSetAnalysisManager.__number_of_rows_and_columns(dataset, jsonfile)
        jsonfile = DataSetAnalysisManager.__missing_values(dataset, jsonfile)
        #jsonfile = DataSetAnalysisManager.__detect_outliers(dataset, jsonfile)
        print(json.dumps(jsonfile))

        with open('controller\app-data\analysis.json', 'w+') as target:
            json.dump(jsonfile, target)
        
    @staticmethod
    def __number_of_rows_and_columns(dataset: pd.DataFrame, jsonfile: defaultdict) -> defaultdict:
        """
        Counts the number of rows and columns of the dataset and adds that information to a JSON file
        ---
        Parameter
        1. dataset to be analyzed
        2. JSON file to write to
        ---
        Return the JSON file with additional data
        """
        rows, columns = dataset.shape

        jsonfile["basic analysis"]["number of rows"] = rows
        jsonfile["basic analysis"]["number of columns"] = columns

        return jsonfile

    @staticmethod
    def __missing_values(dataset: pd.DataFrame, jsonfile: defaultdict) -> defaultdict:
        """
        Counts missing values of each column and row and adds that information to a JSON file
        ---
        Parameter
        1. dataset to be analyzed
        2. JSON file to write to
        ---
        Return the JSON file with additional data
        """
        dataset_missings_columns = dataset.isna().sum()
        for index, value in dataset_missings_columns.items():

            jsonfile["missing values in columns"][index] = value

        dataset_missings_rows = dataset.isna().sum(axis=1)
    
        for index, value in dataset_missings_rows[dataset_missings_rows > len(dataset.columns)*0.5].items():

            jsonfile["rows with many missing values"][index] = value

        
        return jsonfile

    @staticmethod
    def __detect_outliers(dataset: pd.DataFrame, json: defaultdict) -> defaultdict:
        """
        TODO
        """
        pass


    

    


    