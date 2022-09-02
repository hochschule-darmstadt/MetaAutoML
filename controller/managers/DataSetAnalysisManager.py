import os.path

import numpy as np
import math

import pandas as pd
from scipy.stats import spearmanr

class DataSetAnalysisManager:
    """
    Static DataSetAnalysisManager class to analyze the dataset
    """
    def __init__(self, dataset):
        self.__dataset = dataset
        self.__plots = []

    def basicAnalysis(self) -> dict:
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
        print(self.__dataset)
        analysis = {
            "number_of_columns": self.__dataset.shape[1],
            "number_of_rows": self.__dataset.shape[0],
            "na_columns": dict(self.__dataset.isna().sum().items())
        }
        print("[DatasetAnalysisManager]: Calculating high NaN rows..")
        analysis.update({"high_na_rows": DataSetAnalysisManager.__missing_values_rows(self.__dataset)})
        print("[DatasetAnalysisManager]: Calculating outliers..")
        analysis.update({"outlier": DataSetAnalysisManager.__detect_outliers(self.__dataset)})
        print("[DatasetAnalysisManager]: Calculating duplicate columns..")
        analysis.update({"duplicate_columns": DataSetAnalysisManager.__detect_duplicate_columns(self.__dataset)})
        print("[DatasetAnalysisManager]: Calculating duplicate rows..")
        analysis.update({"duplicate_rows": DataSetAnalysisManager.__detect_duplicate_rows(self.__dataset)})

        print("[DatasetAnalysisManager]: Basic dataset analysis finished")
        return analysis

    def advancedAnalysis(self, save_path):
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
        import matplotlib
        matplotlib.use('SVG')
        import matplotlib.pyplot as plt
        plt.ioff()
        print("[DatasetAnalysisManager]: Starting advanced dataset analysis")

        self.__dataset.loc[:, self.__dataset.dtypes == 'object'] = self.__dataset.select_dtypes(['object']).apply(lambda x: x.astype('category'))
        categorical_columns = list(self.__dataset.select_dtypes(['category']).columns) + list(self.__dataset.select_dtypes(['bool']).columns)
        plot_filenames = []

        # Plot distributions of all columns
        print(f"[DatasetAnalysisManager]: Plotting {len(self.__dataset.columns)} columns")
        for i, col in enumerate(list(self.__dataset.columns)):
            self.__make_column_plot(col, save_path)

        # Get processed version of dataset to make calculation of feature correlation using scipy spearmanr possible
        proc_dataset = self.__process_categorical_columns()
        proc_dataset = self.__fill_nan_values(proc_dataset)

        # Get correlations using spearmanr
        corr = spearmanr(proc_dataset).correlation
        # Make correlation plot
        print("[DatasetAnalysisManager]: Plotting correlation matrix")
        self.__make_correlation_matrix_plot(corr, self.__dataset.columns, save_path)

        # Get indices of correlations ordered desc
        indices = self.__largest_indices(corr, (len(proc_dataset.columns) * len(proc_dataset.columns)))

        # Plot features with the highest correlation
        print(f"[DatasetAnalysisManager]: Plotting top 5 feature imbalance plots")
        plotted_indices = []
        for first_col_idx, second_col_index in zip(indices[0], indices[1]):
            # Only plot top 5
            if len(plotted_indices) == 6:
                break
            # If the correlation isn't a col with itself or has already been plotted the other way around -> plot it
            if first_col_idx != second_col_index and [second_col_index, first_col_idx] not in plotted_indices:
                self.__make_feature_imbalance_plot(self.__dataset.columns[first_col_idx],
                                                   self.__dataset.columns[second_col_index],
                                                   save_path)
                plotted_indices.append([first_col_idx, second_col_index])

        print(f"[DatasetAnalysisManager]: Dataset analysis finished, saved {len(self.__plots)} plots")
        return self.__plots


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
    def __detect_outliers(dataset) -> 'list[dict]':
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

        outlier_columns = []
        for column_name in dataset:
            if pd.api.types.is_numeric_dtype(dataset[column_name]):
                Q1 = dataset[column_name].quantile(0.25)
                Q3 = dataset[column_name].quantile(0.75)
                IQR = Q3 - Q1
                filter = (dataset[column_name] <= (Q1 - 2 * IQR)) | (dataset[column_name] >= (Q3 + 2 * IQR))
                outlier_indices = dataset[column_name].loc[filter].index.tolist()
                outlier_columns.append({column_name: outlier_indices})
        
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

    def __process_categorical_columns(self):
        """
        Process categories.
        At a certain step it is necessary to convert string categories and bool into int.
        This is used for the feature correlation matrix, as the scipy spearmanr algorithm used for calculating the
        correlation is incompatible with string categories and bool.

        Return dataset: Copy of dataset stored in the DataSetAnalysisManager with processed categorical values
        """
        dataset = self.__dataset.copy()
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
        fill_value = int("9" * (len(str(int(dataset.max(numeric_only=True).max()))) + 1))
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
        if self.__dataset[colname].dtype.name == "category" or self.__dataset[colname].dtype.name == "bool":
            # Make a bar chart for categorical or bool columns
            df = self.__dataset[colname]
            # Shorten string values if they are too long (Strings of length > 28 are shortened to 25 chars plus '...')
            df = df[df.str.len() < 28].str[:25] + "..."
            df = df.value_counts()
            # Resize figure. The standard size (6.4 x 4.8) works for <50 unique values.
            # Above that: double the size for every 50 extra values
            factor = min(math.ceil(df.shape[0] / 50), 3)
            # If there are too many
            if df.shape[0] < 150:
                df.plot(kind='bar', figsize=(factor * 6.4, 4.8))
            else:
                df.iloc[:150].plot(kind='bar', figsize=(factor * 6.4, 4.8))
                desc = f"This plot shows the first 150 unique values of the {colname} column"
        else:
            # Make a histogram for numerical columns
            self.__dataset[colname].plot(kind='hist')
        plt.title(colname)
        plt.tight_layout()
        #plt.show()
        filename = os.path.join(plot_path, colname + "_column_plot.svg")
        plt.savefig(filename)
        self.__plots.append({"type": "column_plot",
                             "title": colname,
                             "description": desc,
                             "path": filename})

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
        plt.rcParams['figure.figsize'] = [(factor * 6.4), (factor * 4.8)]
        fig = plt.figure()
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
        #plt.show()
        self.__plots.append({"type": "correlation_matrix",
                             "title": "Correlation matrix",
                             "description": "Higher values indicate greater correlation between features",
                             "path": filename})

    def __make_feature_imbalance_plot(self, first_colname, second_colname, plot_path):
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
        samples = 25
        feature_df = self.__dataset.groupby([first_colname, second_colname]).size().reset_index().sort_values(by=[0], ascending=False)
        x_data = list(zip(feature_df[first_colname], feature_df[second_colname]))[:samples]
        x_data = [f"[{x[0]}, {x[1]}]" for x in x_data]
        y_data = list(feature_df[0])[:samples]

        plt.clf()
        plt.bar(x_data, y_data)
        plt.xticks(x_data, labels=x_data, rotation=90)
        plt.xlabel(f"Most common combinations of [{first_colname}, {second_colname}]")
        plt.ylabel(f"Combination count")
        plt.tight_layout()
        #plt.show()
        filename = os.path.join(plot_path, "feature_imbalance_" + first_colname + "_vs_" + second_colname + ".svg")
        plt.savefig(filename)
        self.__plots.append({"type": "feature_imbalance_plot",
                             "title": f"Feature imbalance plot of [{first_colname}, {second_colname}]",
                             "description": f"This plot shows the {samples} most common combinations of the columns "
                                            f"{first_colname} and {second_colname} along with their frequency across "
                                            f"the whole dataset",
                             "path": filename})


    def startLongitudinalDataAnalysis(dataset: pd.DataFrame) -> dict:
        rows, cols = dataset.shape
        return {
            "number_of_columns": cols,
            "number_of_rows": rows,
            "na_columns": {},
            "high_na_rows": [],
            "outlier": [],
            "duplicate_columns": [],
            "duplicate_rows": [],
        }