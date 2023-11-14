
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
##TODO REFACTORING

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
    def __init__(self, dataset_id: str, user_id: str, data_storage: DataStorage, dataset_analysis_lock: ThreadLock, basic_analysis=True, advanced_analysis=True, ydataprofiling_analysis=True):
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
        self.__dataset_analysis_lock = dataset_analysis_lock
        self.__basic_analysis = basic_analysis
        self.__advanced_analysis = advanced_analysis
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

        # Create plot filepath
        self.plot_filepath = os.path.join(os.path.dirname(self.__dataset['path']), "plots")
        os.makedirs(self.plot_filepath, exist_ok=True)
        self.__plots = []

        # Create YData filepath for ydata_profiling
        self.ydata_filepath = os.path.join(os.path.dirname(self.__dataset['path']), "YData")
        os.makedirs(self.ydata_filepath, exist_ok=True)
        self.__report = None


    def run(self):
        analysis = {}
        with self.__dataset_analysis_lock.lock():
            print("[DataSetAnalysisManager]: ENTERING LOCK.")
            schema = self.__dataset_schema_analysis()
            if self.__basic_analysis:
                analysis.update(self.basic_analysis(schema))

            #Only perform analysis when dataset has less than 20 columns
            if self.__advanced_analysis and self.__dataset_df.shape[1] < 20:
                analysis.update({ "plots": self.advanced_analysis()})
            #Only perform YDataProfiling-Report when dataset has less than 80 columns
            if self.__ydataprofiling_analysis and self.__dataset_df.shape[1] < 80:
                analysis.update({ "Report": self.ydataprofiling_analysis()})


            found, dataset = self.__data_storage.get_dataset(self.__user_id, self.__dataset_id)
            analysis_details = dataset["analysis"]
            analysis_details.update(analysis)
            self.__data_storage.update_dataset(self.__user_id, self.__dataset_id, { "analysis": analysis_details, "schema": schema})
            print("[DataSetAnalysisManager]: EXITING LOCK.")

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

    def ydataprofiling_analysis(self):
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

        The generated report is saved as a json file, and its path is stored in MongoDB under analysis > ydata_profiling_report,
        so it can be later displayed in the frontend.

        Returns:
            ProfileReport: A Dataframe with additional parameters
        """
        try:
            from ydata_profiling import ProfileReport
            print("[DatasetAnalysisManager]: Starting ydata-profiling dataset analysis")
            report_filename = "YData_Profile_Report.json"
            report_filepath = os.path.join(self.ydata_filepath, report_filename)
            profile = ProfileReport(self.__dataset_df, title=self.__dataset["path"], html={'style': {'full_width': True}})
            profile.to_file(report_filepath, silent=True)
            print("[DatasetAnalysisManager]: Dataset analysis finished, saved the YData-ProfileReport.")
            self.__report = profile.to_json()
            return self.__report
        except:
            # error case tbd?
            return{}

    def advanced_analysis(self):
        """
        Advanced analysis that produces several plots based on the dataset passed to the DataSetAnalysisManager.
        The plots are saved in the same folder as the dataset, their paths are saved in the mongodb under
        analysis > advanced_analysis_plots so that they can be loaded later for display in the frontend.

        Plots produced are:
            Distribution plots of all features (columns) in the dataset.
            Correlation matrix indicating the correlation of all features in the dataset
            Correlation plots of the 5 features with the highest correlation

        Returns: Array of plot filenames
        """
        # Turn off io of matplotlib as the plots are saved, not displayed
        try:
            import matplotlib
            matplotlib.use('SVG')
            import matplotlib.pyplot as plt
            plt.ioff()
            print("[DatasetAnalysisManager]: Starting advanced dataset analysis")
            if self.__dataset["type"] in [":image"]:
                return
            # Convert all "object" columns to category
            self.__dataset_df.loc[:, self.__dataset_df.dtypes == 'object'] = self.__dataset_df.select_dtypes(['object']).apply(lambda x: x.astype('category'))

            # Get processed version of dataset to make calculation of feature correlation using scipy spearmanr possible
            proc_dataset = self.__process_categorical_columns()
            proc_dataset = self.__fill_nan_values(proc_dataset)
            ## TODO consider to add more analysis feature in case of text, image,...
            if self.__dataset["type"] in [":text"]:
                return
            # Get correlations using spearmanr
            corr = spearmanr(proc_dataset).correlation
            # Make correlation plot
            print("[DatasetAnalysisManager]: Plotting correlation matrix")
            filename = self.__make_correlation_matrix_plot(corr, self.__dataset_df.columns, self.plot_filepath)
            self.__plots.append({"title": "Correlation Matrix", "items": [filename]})
            # Get indices of correlations ordered desc
            indices = self.__largest_indices(corr, (len(proc_dataset.columns) * len(proc_dataset.columns)))

            # Plot features with the highest correlation
            print(f"[DatasetAnalysisManager]: Plotting top 10 feature imbalance plots")
            plotted_indices = []
            category = {"title": "Correlation analysis", "items": []}
            for first_col_idx, second_col_index in zip(indices[0], indices[1]):
                # Only plot top 5
                if len(plotted_indices) == 6:
                    break
                # If the correlation isn't a col with itself or has already been plotted the other way around -> plot it
                if first_col_idx != second_col_index and [second_col_index, first_col_idx] not in plotted_indices:
                    category["items"].append(self.__make_feature_imbalance_plot(self.__dataset_df.columns[first_col_idx],
                                                                                self.__dataset_df.columns[second_col_index],
                                                                                corr[second_col_index, first_col_idx],
                                                                                self.plot_filepath))
                    plotted_indices.append([first_col_idx, second_col_index])
            self.__plots.append(category)

            # Plot distributions of all columns
            print(f"[DatasetAnalysisManager]: Plotting {len(self.__dataset_df.columns)} columns")
            category = {"title": "Column analysis", "items": []}
            for i, col in enumerate(list(self.__dataset_df.columns)):
                category["items"].append(self.__make_column_plot(col, self.plot_filepath))
            self.__plots.append(category)

            print(f"[DatasetAnalysisManager]: Dataset analysis finished, saved {sum(len(x['items']) for x in self.__plots)} plots")
            return self.__plots
        except:
            return {}


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

    def __process_categorical_columns(self):
        """
        Process categories.
        At a certain step it is necessary to convert string categories and bool into int.
        This is used for the feature correlation matrix, as the scipy spearmanr algorithm used for calculating the
        correlation is incompatible with string categories and bool.

        Return dataset: Copy of dataset stored in the DataSetAnalysisManager with processed categorical values
        """
        dataset = self.__dataset_df.copy()
        for i, dtype in enumerate(dataset.dtypes):
            if dtype.name == "category":
                # Process the corresponding column
                # Get all unique values in the category column
                unique_values = dataset.iloc[:, i].unique()
                # Replace values in dataframe with their index in the list
                dataset.iloc[:, i] = dataset.iloc[:, i].map({val: i for i, val in enumerate(unique_values.categories.values)})
            if dtype.name == "bool":
                # Bool values have to be processed too
                unique_values = [False, True]
                dataset.iloc[:, i] = dataset.iloc[:, i].map({val: i for i, val in enumerate(unique_values)})

        return dataset

    def __fill_nan_values(self, dataset):
        """
        Fill nan values.
        Fill with 9999... with the length of the max number of digits in the df + 1.
        This is done in this convoluted way to fill the na values of both categorical and non-categorical columns with
        a value that is guaranteed to not be anywhere in the dataframe.

        Return dataset: Dataset with filled nan values
        """
        # TODO refactoring
        # handle in case most of the data are not numeric
        # consider using this function only where numerical values are avaialbe
        max_value = dataset.max(numeric_only=True).max() # max value in data set
        if pd.isna(max_value):
            max_value = 0
        fill_value = int("9" * (len(str(int(max_value))) + 1))
        for col in dataset.columns:
            if dataset[col].dtype.name == "category":
                # Category cols require special handling
                dataset[col] = dataset[col].cat.add_categories(fill_value).fillna(fill_value)
            else:
                dataset[col] = dataset[col].fillna(fill_value)

        return dataset

    def __largest_indices(self, ary, n):
        """Returns the n largest indices from a numpy array."""
        flat = ary.flatten()
        indices = np.argpartition(flat, -n)[-n:]
        indices = indices[np.argsort(-flat[indices])]
        return np.unravel_index(indices, ary.shape)

    def __make_column_plot(self, colname, plot_path):
        """
        Plot a single feature (column) of the dataframe. If the feature is categorical or bool it is plotted as a bar
        chart, otherwise it is plotted as a histogram.
        ---
        Param colname: Name of column to plot.
        Param plot_path: Path where the plots are saved.
        ---
        Returns filename: Filepath of the produced plot.
        """
        import matplotlib
        matplotlib.use('SVG')
        import matplotlib.pyplot as plt
        plt.clf()
        desc = f"This plot shows the {colname} column"
        if self.__dataset_df[colname].dtype.name == "category" or self.__dataset_df[colname].dtype.name == "bool":
            # Make a bar chart for categorical or bool columns
            df = self.__dataset_df[colname].astype(str)
            # Shorten string values if they are too long (Strings of length > 28 are shortened to 25 chars plus '...')
            df[df.str.len() > 28] = df[df.str.len() > 28].str[:25] + "..."
            df = df.value_counts()
            # Resize figure. The standard size (6.4 x 4.8) works for <50 unique values.
            # Above that: double the size for every 50 extra values up to a factor of 2x
            factor = min(math.ceil(df.shape[0] / 50), 2)
            # If there are too many
            if df.shape[0] < 100:
                df.plot(kind='bar',
                        figsize=(factor * PLT_XVALUE, PLT_YVALUE),
                        xlabel=f"Value of {colname}",
                        ylabel="Frequency")
                desc = f"This is a frequency diagram of the {colname} column. The Frequency indicates how often the " \
                       f"corresponding value is found within the dataset."
            else:
                df.iloc[:100].plot(kind='bar',
                                   figsize=(factor * PLT_XVALUE, PLT_YVALUE),
                                   xlabel=f"Value of {colname}",
                                   ylabel="Frequency")
                desc = f"This shows the 100 most common unique values of the {colname} column along with their " \
                       f"frequency. The Frequency indicates how often the corresponding value is found within the " \
                       f"dataset. This plot only shows a subset of values as the {colname} column has too many " \
                       f"distinct values."
        else:
            # Make a histogram for numerical columns
            self.__dataset_df[colname].plot(kind='hist',
                                         figsize=(PLT_XVALUE, PLT_YVALUE),
                                         xlabel=f"Distribution of {colname}",
                                         ylabel="Frequency")
            desc = f"This is a histogram of the {colname} column. It shows the distribution of the {colname} " \
                   f"values."
        plt.title(colname)
        plt.tight_layout()
        filename = os.path.join(plot_path, self.escape_column_name(colname) + "_column_plot.svg")
        plt.savefig(filename)
        plt.clf()
        plt.close('all')
        return {"type": "column_plot",
                "title": colname,
                "description": desc,
                "path": filename}

    def __make_correlation_matrix_plot(self, corr, columns, plot_path):
        """
        Plot a correlation matrix visualizing the correlation between all features of the dataset. The correlation score
        was calculated with the scipy spearmanr algorithm.
        ---
        Param corr: Correlations from the spearmanr algorithm.
        Param columns: List of column names.
        Param plot_path: Path where the plots are saved.
        ---
        """
        import matplotlib
        matplotlib.use('SVG')
        import matplotlib.pyplot as plt
        plt.clf()
        # Resize figure. The standard size (6.4 x 4.8) works for <20 cols.
        # Above that: double the size for every 20 extra columns
        factor = math.ceil(len(columns) / 20)
        fig = plt.figure(figsize=((factor * PLT_XVALUE), (factor * PLT_YVALUE)))
        ax = fig.add_subplot(111)
        cax = ax.matshow(
            corr,
            cmap='coolwarm',
            vmin=-1,
            vmax=1)
        fig.colorbar(cax)
        ticks = np.arange(0, len(columns), 1)
        ax.set_xticks(ticks)
        plt.xticks(rotation=90)
        ax.set_yticks(ticks)
        ax.set_xticklabels(columns)
        ax.set_yticklabels(columns)
        plt.tight_layout()
        filename = os.path.join(plot_path, "correlation_matrix.svg")
        plt.savefig(filename)
        plt.clf()
        plt.close('all')
        return {"type": "correlation_matrix",
                "title": "Correlation matrix",
                "description": "The correlation matrix visualizes the correlation between columns in the dataset. "
                               "Higher values indicate greater correlation between features. ",
                "path": filename}

    def __make_feature_imbalance_plot(self, first_colname, second_colname, correlation_value, plot_path):
        """
        Plot feature imbalance plot between two columns. The feature imbalance plot shows the most common combinations
        the values of two features (columns) can have along with their frequency.
        ---
        Param first_colname: Name of first column.
        Param second_colname: Name of second column.
        Param plot_path: Path where the plots are saved.
        ---
        """
        import matplotlib
        matplotlib.use('SVG')
        import matplotlib.pyplot as plt
        samples = 100

        feature_df = self.__dataset_df.groupby([first_colname, second_colname]).size().reset_index().sort_values(by=[0], ascending=False)
        x_data = list(zip(feature_df[first_colname].astype(str), feature_df[second_colname].astype(str)))[:samples]
        x_data = [f"[{(x[0][:6] + '..') if len(x[0]) > 8 else x[0]}, {(x[1][:6] + '..') if len(x[1]) > 8 else x[1]}]" for x in x_data]
        y_data = list(feature_df[0])[:samples]

        plt.clf()
        # Resize figure. The standard size (6.4 x 4.8) works for <50 unique values.
        # Above that: double the size for every 50 extra values up to a factor of 2x
        factor = min(math.ceil(len(y_data) / 50), 2)
        plt.figure(figsize=((factor * PLT_XVALUE), PLT_YVALUE))
        plt.bar(x_data, y_data)
        plt.title(f"Correlaton plot of [{first_colname}, {second_colname}]")
        plt.xticks(x_data, labels=x_data, rotation=90)
        plt.xlabel(f"Most common combinations of [{first_colname}, {second_colname}]")
        plt.ylabel(f"Frequency")
        plt.tight_layout()
        filename = os.path.join(plot_path, "feature_imbalance_" + self.escape_column_name(first_colname) + "_vs_" + self.escape_column_name(second_colname) + ".svg")
        plt.savefig(filename)
        plt.clf()
        plt.close('all')
        return {"type": "feature_imbalance_plot",
                "title": f"Correlation plot of [{first_colname}, {second_colname}]",
                "description": f"This plot shows the {len(x_data)} most common combinations of the columns "
                               f"{first_colname} and {second_colname} ordered by their frequency."
                               f"These two columns have a correlation value of {round(correlation_value, 2)}",
                "path": filename}


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
