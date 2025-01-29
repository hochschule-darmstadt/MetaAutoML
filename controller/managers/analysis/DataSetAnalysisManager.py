import os
from threading import Thread
import pandas as pd
from feature_engine.selection import DropConstantFeatures, DropDuplicateFeatures, SmartCorrelatedSelection
from DataStorage import DataStorage
from CsvManager import CsvManager
from tqdm import tqdm

class DataSetAnalysisManager:
    def __init__(self, dataset_id: str, user_id: str, data_storage: DataStorage, basic_analysis=True, ydataprofiling_analysis=True):
        super().__init__()
        self.__dataset_id = dataset_id
        self.__user_id = user_id
        self.__data_storage = data_storage
        self.__basic_analysis = basic_analysis
        self.__ydataprofiling_analysis = ydataprofiling_analysis

        # Load dataset
        self.__dataset = self.__load_dataset()
        self.__dataset_df = self.__load_dataframe()

        # Create YData filepath for ydata_profiling
        self.ydata_filepath = os.path.join(os.path.dirname(self.__dataset['path']), "YData")
        os.makedirs(self.ydata_filepath, exist_ok=True)

    def __load_dataset(self):
        found, dataset = self.__data_storage.get_dataset(self.__user_id, self.__dataset_id)
        if dataset["type"] == ":image":
            self.__ydataprofiling_analysis = False
        return dataset

    def __load_dataframe(self):
        dataset_path = self.__dataset["path"]
        file_config = self.__dataset["file_configuration"]
        schema = self.__dataset.get("schema", {})

        try:
            return CsvManager.read_dataset(dataset_path, file_config, schema)
        except pd.errors.ParserError:
            return CsvManager.read_dataset(dataset_path, file_config, schema)

    def run_analysis(self):
        analysis = {}
        schema = self.__dataset_schema_analysis()

        if self.__basic_analysis:
            analysis.update(self.basic_analysis(schema))
            self.__update_dataset_analysis(analysis, schema)

        if self.__ydataprofiling_analysis:
            report = self.ydataprofiling_analysis()
            analysis.update({"report_html_path": report[0], "report_json_path": report[1]})

        self.__update_dataset_analysis(analysis, schema)

    def __update_dataset_analysis(self, analysis, schema):
        current_dateset = self.__data_storage.get_dataset(self.__user_id, self.__dataset_id)[1]
        if current_dateset:
            analysis_details = current_dateset["analysis"]
            analysis_details.update(analysis)
            self.__data_storage.update_dataset(self.__user_id, self.__dataset_id, {"analysis": analysis_details, "schema": schema})

    def __dataset_schema_analysis(self) -> dict:
        if self.__dataset["type"] in [":tabular", ":text", ":time_series"]:
            return CsvManager.get_default_dataset_schema(self.__dataset["path"], self.__dataset["file_configuration"])
        return {}

    def basic_analysis(self, schema) -> dict:
        analysis = {
            "size_bytes": self.__get_size_bytes(self.__dataset["path"]),
            "creation_date": os.path.getmtime(self.__dataset["path"])
        }

        if self.__dataset["type"] == ":time_series_longitudinal":
            rows, cols = self.__dataset_df.shape
            analysis.update({"number_of_columns": cols, "number_of_rows": rows})
        elif self.__dataset["type"] in [":tabular", ":text", ":time_series"]:
            analysis.update({
                "number_of_columns": self.__dataset_df.shape[1],
                "number_of_rows": self.__dataset_df.shape[0],
                "missings_per_column": self.__dataset_df.isna().sum().to_dict(),
                "missings_per_row": self.__missing_values_rows(self.__dataset_df),
                "outlier": self.__detect_outliers(self.__dataset_df, schema),
                "duplicate_columns": self.__detect_duplicate_columns(self.__dataset_df),
                "duplicate_rows": self.__detect_duplicate_rows(self.__dataset_df),
                "irrelevant_features": self.__detect_irrelevant_features(self.__dataset_df)
            })
        return analysis

    def ydataprofiling_analysis(self) -> tuple:
        from ydata_profiling import ProfileReport
        print("[DatasetAnalysisManager]: Starting ydata-profiling dataset analysis")
        report_filename = "YData_Profile_Report.html"
        report_filepath = os.path.join(self.ydata_filepath, report_filename)
        profile = ProfileReport(self.__dataset_df, title="Advance Analysis", html={'style': {'full_width': True}}, minimal=False)
        profile.to_file(report_filepath, silent=True)
        report_filename_json = "YData_Profile_Report.json"
        report_filepath_json = os.path.join(self.ydata_filepath, report_filename_json)
        profile.to_file(report_filepath_json, silent=True)
        print("[DatasetAnalysisManager]: Dataset analysis finished, saved the YData-ProfileReport.")
        return (report_filepath, report_filepath_json)

    @staticmethod
    def __missing_values_rows(dataset) -> list:
        return dataset.index[dataset.isna().sum(axis=1) > (len(dataset.columns) * 0.5)].tolist()

    @staticmethod
    def __detect_irrelevant_features(dataset) -> list:
        old_columns = dataset.columns.tolist()
        dataframe = dataset.dropna()
        if not dataframe.empty:
            constant_features = DropConstantFeatures(tol=0.998)
            dataframe = constant_features.fit_transform(dataframe)
            # Identify duplicate columns with progress tracking
            duplicate_columns = []
            for i, col in tqdm(enumerate(dataframe.columns), total=dataframe.shape[1], desc="Removing duplicate columns"):
                for j in range(i + 1, len(dataframe.columns)):
                    if dataframe.iloc[:, i].equals(dataframe.iloc[:, j]):
                        duplicate_columns.append(dataframe.columns[j])

            # Remove duplicate columns
            dataframe = dataframe.drop(columns=duplicate_columns)

            #dataframe = dataframe.loc[:, ~dataframe.T.duplicated()]
        #duplicate_features = DropDuplicateFeatures()
        #dataframe = duplicate_features.fit_transform(dataframe)
        numerical_columns = dataframe.select_dtypes(include=['number']).columns
        try:
            if len(numerical_columns) >= 1:
                correlated_features = SmartCorrelatedSelection()
                dataframe = correlated_features.fit_transform(dataframe)
        except Exception:
            #TODO some dataset have features but then the corrlatedsection doesnt have any and crashes
            pass
        finally:
            new_columns = dataframe.columns.tolist()
            return [col for col in old_columns if col not in new_columns]

    @staticmethod
    def __detect_outliers(dataset, schema) -> dict:
        outlier_columns = {}
        for column_name, dt in schema.items():
            if dt['datatype_detected'] in [':integer', ':float']:
                Q1 = dataset[column_name].quantile(0.25)
                Q3 = dataset[column_name].quantile(0.75)
                IQR = Q3 - Q1
                filter = (dataset[column_name] < (Q1 - 2 * IQR)) | (dataset[column_name] > (Q3 + 2 * IQR))
                outlier_indices = dataset[column_name].loc[filter].index.tolist()
                if outlier_indices:
                    outlier_columns[column_name] = outlier_indices[:100]
        return outlier_columns

    @staticmethod
    def __detect_duplicate_columns(dataset) -> list:
        return [(dataset.columns[i], dataset.columns[j])
                for i in range(len(dataset.columns))
                for j in range(i+1, len(dataset.columns))
                if dataset.iloc[:, i].equals(dataset.iloc[:, j])]

    @staticmethod
    def __detect_duplicate_rows(dataset) -> list:
        df = dataset[dataset.duplicated(keep=False)]
        return df.groupby(list(df)).apply(lambda x: tuple(x.index)).values.tolist()

    @staticmethod
    def __get_size_bytes(path='.'):
        if os.path.isfile(path):
            return os.path.getsize(path)
        return sum(os.path.getsize(os.path.join(dirpath, f))
                   for dirpath, _, filenames in os.walk(path)
                   for f in filenames if not os.path.islink(os.path.join(dirpath, f)))

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
        return colname.replace('/', '')
