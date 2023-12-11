
from genericpath import isfile
import os.path
from threading import Thread
import numpy as np
import math
import json
import pandas as pd
from scipy.stats import spearmanr
from sktime.datasets import load_from_tsfile_to_dataframe
from DataStorage import DataStorage
from ThreadLock import ThreadLock
from CsvManager import CsvManager
from feature_engine.selection import DropConstantFeatures, DropDuplicateFeatures, SmartCorrelatedSelection

# Config for matplotlib plot sizing. These values are interpreted as pixels / 100.
# So a Y value of 4 means that the plots will be 400px high.
# This is configured as vars here because the plots are capable of resizing themselves up to a factor of 3x.
# The value this is set to should be correlated to the value in the frontend
PLT_XVALUE = 6.5
PLT_YVALUE = 5

class DataSetAnalysisManager(Thread):
    """
    Static DataSetAnalysisManager class to analyze the dataset
    """
    def __init__(self, dataset_id: str, user_id: str, data_storage: DataStorage, basic_analysis=True, ydataprofiling_analysis=True):
        super(DataSetAnalysisManager, self).__init__()
        # Setup config
        self.__dataset_id = dataset_id
        self.__user_id = user_id
        found, dataset = data_storage.get_dataset(user_id, dataset_id)
        file_config = dataset["file_configuration"]
        self.__dataset = dataset
        #delimiters = {
        #    "comma":        ",",
        #    "semicolon":    ";",
        #    "space":        " ",
        #    "tab":          "\t",
        #}
        self.__data_storage = data_storage
        self.__basic_analysis = basic_analysis
        self.__ydataprofiling_analysis = ydataprofiling_analysis
        # Load dataset
        if self.__dataset["type"] == ":time_series_longitudinal":
            self.__dataset_df = load_from_tsfile_to_dataframe(self.__dataset["path"], return_separate_X_and_y=False)
        elif self.__dataset["type"] in [":tabular", ":text", ":time_series"]:
            try:
                self.__dataset_df = CsvManager.read_dataset(self.__dataset["path"], dataset["file_configuration"], dataset["schema"])
                #self.__dataset_df = pd.read_csv(self.__dataset["path"],
                #                             delimiter=delimiters[file_config['delimiter']],
                #                             skiprows=(file_config['start_row'] - 1),
                #                             escapechar=file_config['escape_character'],
                #                             decimal=file_config['decimal_character'],
                #                             engine="python",
                #                             index_col=False,
                #                             encoding=file_config['encoding'],
                #                             encoding_errors='ignore')
            except pd.errors.ParserError as e:
                # As the pandas python parsing engine sometimes fails: Retry with standard (c) parser engine.
                self.__dataset_df = CsvManager.read_dataset(self.__dataset["path"], dataset["file_configuration"], dataset["schema"])
                #TODO still necessary. since we use frontend encoding detection
                #pd.read_csv(self.__dataset["path"],
                #                             delimiter=delimiters[file_config['delimiter']],
                #                             skiprows=(file_config['start_row'] - 1),
                #                             escapechar=file_config['escape_character'],
                #                             decimal=file_config['decimal_character'],
                #                             index_col=False)
        else:
            pass

        # Create YData filepath for ydata_profiling
        self.ydata_filepath = os.path.join(os.path.dirname(self.__dataset['path']), "YData")
        os.makedirs(self.ydata_filepath, exist_ok=True)



    def run(self):
        analysis = {}
        schema = self.__dataset_schema_analysis()
        if self.__basic_analysis:
            analysis.update(self.basic_analysis(schema))

        #Perform YDataProfiling-Report without minimal option when dataset has less than 80 columns
        if self.__ydataprofiling_analysis and self.__dataset_df.shape[1] < 80:
            report = self.ydataprofiling_analysis(minimal_Opt=False) # tuple (html_path, json_path)
        else:
            # minimal calculation option activated for datasets with more than 80 columns
            report = self.ydataprofiling_analysis(minimal_Opt=True) # tuple (html_path, json_path)

        analysis.update({"report_html_path": report})
        found, dataset = self.__data_storage.get_dataset(self.__user_id, self.__dataset_id)
        analysis_details = dataset["analysis"]
        analysis_details.update(analysis)
        self.__data_storage.update_dataset(self.__user_id, self.__dataset_id, {"analysis": analysis_details, "schema": schema})


    def __dataset_schema_analysis(self) -> dict:

        if self.__dataset["type"] in [":tabular", ":text", ":time_series"]:
            #generate preview of tabular and text dataset
            #previewDf = pd.read_csv(filename_dest)
            #previewDf.head(50).to_csv(filename_dest.replace(".csv", "_preview.csv"), index=False)
            #causes error with different delimiters use normal string division
            #self.__log.debug("__dataset_schema_analysis: dataset is of CSV type: generating csv file configuration...")
            return CsvManager.get_default_dataset_schema(self.__dataset["path"], self.__dataset["file_configuration"])
        return {}

    def basic_analysis(self, schema) -> dict:
        """
        Basic analysis, results are returned as dict
        Analyzed are:
            "number_of_columns": Number of columns
            "number_of_rows": Number of rows
            "na_columns": Missing value counts for each column
            "high_na_rows": Missing value counts for each row
            "outlier": Outlier detection
            "duplicate_columns": Duplicate columns
            "duplicate_rows": Duplicate rows

        Return a python dictionary containing dataset analysis
        """
        print("[DatasetAnalysisManager]: Starting basic dataset analysis")
        #print(self.__dataset)
        analysis = {
                "size_bytes": DataSetAnalysisManager.__get_size_bytes(self.__dataset["path"]),
                "creation_date": os.path.getmtime(self.__dataset["path"])
        }
        if self.__dataset["type"] == ":time_series_longitudinal":
            rows, cols = self.__dataset_df.shape
            analysis.update({
                "number_of_columns": cols,
                "number_of_rows": rows
            })
        elif self.__dataset["type"] in [":tabular", ":text", ":time_series"]:
            analysis.update({
                "number_of_columns": self.__dataset_df.shape[1],
                "number_of_rows": self.__dataset_df.shape[0],
                "missings_per_column": dict(self.__dataset_df.isna().sum().items()),
                "missings_per_row": DataSetAnalysisManager.__missing_values_rows(self.__dataset_df),
                "outlier": DataSetAnalysisManager.__detect_outliers(self.__dataset_df, schema),
                "duplicate_columns": DataSetAnalysisManager.__detect_duplicate_columns(self.__dataset_df),
                "duplicate_rows": DataSetAnalysisManager.__detect_duplicate_rows(self.__dataset_df),
                "irrelevant_features": DataSetAnalysisManager.__detect_irrelevant_features(self.__dataset_df)
            })
        elif self.__dataset["type"] == ":image":
            pass

        print("[DatasetAnalysisManager]: Basic dataset analysis finished")
        return analysis

    def ydataprofiling_analysis(self, minimal_Opt):
        """
        Generates a YData-Profiling report for the provided dataset. This report offers a comprehensive overview
        of the data through detailed statistical analyses and visualizations of each feature in the dataset.
        It is useful for gaining insights into the data structure, missing values, data types, and potential
        correlations between various features.

        The report includes:
            - Summary tables with key statistics for each feature.
            - Histograms and boxplots to visualize distributions.
            - Heatmaps for correlations between features.
            - Detailed information on missing values and their distribution in the dataset.

        The generated report is saved as a html file, and its path is stored in MongoDB under analysis > ydata_profiling_report. The Preview
        gets extracted from the json file, also safed in the MongoDB (ydata_profiling_json)

        Returns:
            html path for ydataprofiling report
        """
        try:
            from ydata_profiling import ProfileReport
            print("[DatasetAnalysisManager]: Starting ydata-profiling dataset analysis")

            report_filename = "YData_Profile_Report.html"
            report_filepath = os.path.join(self.ydata_filepath, report_filename)
            profile = ProfileReport(self.__dataset_df, title="Advance Analysis", html={'style': {'full_width': True}})
            profile.to_file(report_filepath, silent=True)
            print("[DatasetAnalysisManager]: Dataset analysis finished, saved the YData-ProfileReport.")
            return report_filepath
        except:
            return{}


    @staticmethod
    def __missing_values_rows(dataset) -> 'list[int]':
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
    def __detect_irrelevant_features(dataset) -> 'list[str]':
        """
        Detects irrelevant features in a dataset
        ---
        Parameter
        1. dataset to be analyzed
        ---
        Return a list of strings each representing an irrelevant feature.
        """
        old_columns_list = dataset.columns.tolist()

        dataframe = dataset
        #The DropConstantFeatures does not tolerate NaN vales, drop first
        #If the datadrame is empty we can not use it, and reset the dataframe and only do the other steps
        dataframe = dataframe.dropna()
        if dataframe.empty == False:
            constant_features = DropConstantFeatures(tol=0.998)  # Standard-Toleranzwert
            dataframe = constant_features.fit_transform(dataframe)
        else:
            dataframe = dataset
        duplicate_features = DropDuplicateFeatures()
        dataframe = duplicate_features.fit_transform(dataframe)

        numerical_columns = dataframe.select_dtypes(include=['number']).columns
        if len(numerical_columns) >= 1:
            correlated_features = SmartCorrelatedSelection()
            dataframe = correlated_features.fit_transform(dataframe)

        new_columns_list = dataframe.columns.tolist()

        irrelevant_features = []
        for element in old_columns_list:
            if element not in new_columns_list:
                irrelevant_features.append(element)
        return irrelevant_features

    @staticmethod
    def __detect_outliers(dataset, schema) -> 'dict':
        """
        Detects outliers in all columns in a dataset containing floats.
        Outliers are determined using the inter quartile range (IQR) with an outlier being classified as being above
        or below 2 * IQR
        ---
        Parameter
        1. dataset to be analyzed
        ---
        Return a list containing the indices of outliers for each numerical column
        """
        import pandas as pd

        outlier_columns = {}

        for column_name, dt in schema.items():
            if dt['datatype_detected'] in [':integer', ':float']:
                Q1 = dataset[column_name].quantile(0.25)
                Q3 = dataset[column_name].quantile(0.75)
                IQR = Q3 - Q1
                filter = (dataset[column_name] < (Q1 - 2 * IQR)) | (dataset[column_name] > (Q3 + 2 * IQR))
                outlier_indices = dataset[column_name].loc[filter].index.tolist()
                #Only count first 100 indexes and only add columns that have outliers to avoid empty lists
                if len(outlier_indices) == 0:
                    continue
                elif len(outlier_indices) > 100:
                    outlier_columns.update({column_name: outlier_indices[0:99]})
                else:
                    outlier_columns.update({column_name: outlier_indices})

        #for column_name in dataset:
        #    if pd.api.types.is_numeric_dtype(dataset[column_name]):
        #        Q1 = dataset[column_name].quantile(0.25)
        #        Q3 = dataset[column_name].quantile(0.75)
        #        IQR = Q3 - Q1
        #        filter = (dataset[column_name] < (Q1 - 2 * IQR)) | (dataset[column_name] > (Q3 + 2 * IQR))
        #        outlier_indices = dataset[column_name].loc[filter].index.tolist()
        #       outlier_columns.append({column_name: outlier_indices})

        return outlier_columns

    @staticmethod
    def __detect_duplicate_columns(dataset) -> 'list[tuple]':
        """
        Detects duplicate columns in a dataset
        ---
        Parameter
        1. dataset to be analyzed
        ---
        Return a list of tuples each containing a pair of duplicate column indices.
        """
        duplicate_column_list = []

        for idx_a, column_a in enumerate(dataset.columns):
            for idx_b, column_b in enumerate(dataset.columns):
                if idx_a == idx_b:
                    continue
                values_a = dataset[column_a]
                values_b = dataset[column_b]
                if values_a.equals(values_b):
                    if (column_a, column_b) not in duplicate_column_list and (column_b, column_a) not in duplicate_column_list:
                        duplicate_column_list.append((column_a, column_b))

        return duplicate_column_list

    @staticmethod
    def __detect_duplicate_rows(dataset) -> 'list[tuple]':
        """
        Detects duplicate rows
        ---
        Parameter
        1. dataset to be analyzed
        ---
        Return a list of tuples each containing a list of duplicate row indices
        """
        # Filter dataset, this only keeps rows that are duplicated. keep=False does keep every occurrence of the
        # duplicated row (instead of first or last)
        df = dataset[dataset.duplicated(keep=False)]
        # Group the filtered (only duplicates) dataset by all values so all the duplicated rows are grouped.
        # Then save the indices of the grouped items into tuples.
        return df.groupby(list(df)).apply(lambda x: tuple(x.index)).values.tolist()

    @staticmethod
    def __get_size_bytes(path='.'):
        total_size = 0
        if os.path.isfile(path):
            total_size = os.path.getsize(path)
        else:
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    # skip if it is symbolic link
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)

        return total_size


    def start_longitudinal_data_analysis(self) -> dict:
        rows, cols = self.__dataset_df.shape
        return {
            "number_of_columns": cols,
            "number_of_rows": rows,
            "na_columns": {},
            "high_na_rows": [],
            "outlier": [],
            "duplicate_columns": [],
            "duplicate_rows": [],
            "irrelevant_features": [],
        }


    def escape_column_name(self, colname: str) -> str:
        # remove / in column names to avoid path error
        return colname.replace('/', '')
