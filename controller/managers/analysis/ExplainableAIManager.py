import json
import os
import pandas as pd
import threading
import sys
import numpy as np
from threading import Lock, Thread
from AdapterManager import AdapterManager
from ControllerBGRPC import *
from DataStorage import DataStorage
from ThreadLock import ThreadLock
from CsvManager import CsvManager
from explainerdashboard import ClassifierExplainer, ExplainerDashboard
import re

def make_svg_waterfall_plot(base_value, shap_values, X, path, filename_detail):
    import shap
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    filename = os.path.join(path, f"waterfall_{filename_detail}.svg")
    # Shorten string values if they are too long (Strings of length > 28 are shortened to 25 chars plus '...')
    X = X.astype(str)
    X[X.str.len() > 10] = X[X.str.len() > 10].str[:8] + ".."
    shap.waterfall_plot(
        shap.Explanation(values=shap_values,
                         base_values=base_value,
                         data=X,
                         feature_names=X.index.tolist()),
        max_display=10,
        show=False)
    plt.tight_layout()
    plt.savefig(filename)
    plt.clf()
    return filename


def make_svg_beeswarm_plot(base_value, shap_values, X, path, filename_detail):
    import shap
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    filename = os.path.join(path, f"beeswarm_{filename_detail}.svg")
    shap.plots.beeswarm(shap.Explanation(values=shap_values,
                                         base_values=base_value,
                                         data=X,
                                         feature_names=X.columns.tolist()),
                        show=False)
    plt.tight_layout()
    plt.savefig(filename)
    plt.clf()
    return filename


def make_svg_summary_plot(shap_values, X, classnames, path):
    import shap
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    filename = os.path.join(path, "summary_bar.svg")
    shap.summary_plot(shap_values=shap_values, features=X, plot_type='bar', show=False, class_names=classnames)
    plt.tight_layout()
    plt.savefig(filename)
    plt.clf()
    return filename


def plot_tabular_classification(dataset_X, dataset_Y, target, no_samples, explainer, shap_values, plot_path):
    """
    Plot the produced explanation by using the functionality provided by shap.
    This produces 4 kinds of plots: force plots, waterfall plots, which look at one row of the source data and beeswarm
        and summary plots that look at a number of rows from the input dataset.
        Force, waterfall and beeswarm plots are done for each individual target class of the classification while the
        summary plot is done once for the whole model as it aggregates all of them.
    ---
    dataset_X: Pandas DataFrame of the dataset without the target column.
    dataset_Y: Pandas Series of the dataset target column.
    target: Name of the target column. This is only used for generating the plot descriptions.
    no_samples: Number of samples used in the shap explanation. This is only used for generating the plot descriptions.
    explainer: SHAP explainer object.
    shap_values: Array of shap values produced by the explainer.
    plot_path: Path where the plots should be saved.
    """
    plots = []
    dataset_X[dataset_X.select_dtypes(['bool']).columns] = dataset_X[dataset_X.select_dtypes(['bool']).columns].astype(str)
    classlist = list(val for val in dataset_Y.unique())

    filename = make_svg_summary_plot(shap_values, dataset_X, classlist, plot_path)
    plots.append({"type": "summary_plot",
                  "title": f"Summary plot",
                  "description": f"The summary plot aggregates the importance of all features towards all classes. "
                                 f"The higher the x-axis value is for a feature the more significance this feature "
                                 f"has for the model. The color split within the bars indicates for which class "
                                 f"this feature is important. If the bar coloring is split evenly the values of "
                                 f"this feature are equally important for all classes. If it is skewed towards one "
                                 f"color the values of this feature are only important when deciding for the one "
                                 f"corresponding class.",
                  "path": filename})

    for class_idx, class_value in enumerate(classlist):
        row_idx = int(dataset_Y[dataset_Y == class_value].index[0])

        filename = make_svg_waterfall_plot(base_value=explainer.expected_value[class_idx],
                                           shap_values=shap_values[class_idx][row_idx], X=dataset_X.iloc[row_idx],
                                           path=plot_path,
                                           filename_detail=f"{target}_{class_value}")
        plots.append({"type": "waterfall_plot",
                      "title": f"Waterfall plot of {target} = {class_value}",
                      "description": f"The waterfall plot shows the significance of certain features within the dataset"
                                     f" by their impact on the model. This is done by looking at one row within the "
                                     f"dataset. The values quantify this impact. From the base value certain features "
                                     f"'push' the model to make a certain decision. In this case the analysis looks "
                                     f"only at row {row_idx} of the dataset where the value of {target} "
                                     f"is {class_value} and so features that push the model towards this decision are "
                                     f"indicated by higher values and red coloring while features that point towards "
                                     f"other classes are marked in blue.",
                      "path": filename})

        filename = make_svg_beeswarm_plot(base_value=explainer.expected_value[class_idx],
                                          shap_values=shap_values[class_idx], X=dataset_X, path=plot_path,
                                          filename_detail=f"{class_value}")
        plots.append({"type": "beeswarm_plot",
                      "title": f"Beeswarm plot of {target} = {class_value}",
                      "description": f"The beeswarm plot shows the significance of certain features within the dataset "
                                     f"by their impact on the model. This plot looks at {no_samples} samples from the "
                                     f"dataset and aggregates their impact. This plot specifically looks at {target} = "
                                     f"{class_value}. The shap values on the x axis indicate the impact. If the value "
                                     f"is positive this value adds to the models confidence in predicting {class_value}"
                                     f". The color of the dots indicate the feature values. So a red dot on the right "
                                     f"side of the plot means that a high value of this feature pushes the model "
                                     f"towards  predicting {class_value}. If a feature is in the middle it does not "
                                     f"have any influence on the prediction the model makes, regardless of its value.\n"
                                     f"If a feature is greyed out it means that it is a categorical feature and can "
                                     f"therefore not be analyzed by its value.",
                      "path": filename})

    return plots


def feature_preparation(X, features, datetime_format, is_prediction=False):
    target = ""
    is_target_found = False
    for column, dt in features:
        #During the prediction process no target column was read, so unnamed column names will be off by -1 index,
        #if they are located after the target column within the training set, their index must be adjusted
        if re.match(r"Column[0-9]+", column) and is_target_found == True and is_prediction == True:
            column_index = re.findall('[0-9]+', column)
            column_index = int(column_index[0])
            X.rename(columns={f"Column{column_index-1}": column}, inplace=True)

        #Check if column is to be droped either its role is ignore or index
        if dt.get("role_selected", "") == ":ignore" or dt.get("role_selected", "") == ":index":
            X.drop(column, axis=1, inplace=True)
            continue
        #Get column datatype
        datatype = dt.get("datatype_selected", "")
        if datatype == "":
            datatype = dt["datatype_detected"]

        #during predicitons we dont have a target column and must avoid casting it
        if dt.get("role_selected", "") == ":target" and is_prediction == True:
            is_target_found = True
            continue

        if datatype == ":categorical":
            X[column] = X[column].astype('category')
        elif datatype == ":boolean":
            X[column] = X[column].astype('bool')
        elif datatype == ":integer":
            X[column] = X[column].astype('int')
        elif datatype == ":float":
            X[column] = X[column].astype('float')
        elif datatype == ":datetime":
            X[column] = pd.to_datetime(X[column], format=datetime_format)
        elif datatype == ":string":
            X[column] = X[column].astype('object')

        #Get target column
        if dt.get("role_selected", "") == ":target":
            target = column
            is_target_found = True

    if is_prediction == True:
        y = pd.Series()
    else:
        y = X[target]
        X.drop(target, axis=1, inplace=True)

    return X, y


class ExplainableAIManager:
    def __init__(self, data_storage: DataStorage):
        self.__threads = []
        self.startExplainerDashboard()

    def startExplainerDashboard(self, path):
        def callback():    
            filepath = "./binary_dashboard.dill"   # os.path.join(path, "binary_dashboard.dill")
            dashboard = ExplainerDashboard(ClassifierExplainer.from_file(filepath))
            dashboard.run(8045)
            self.__threads.remove(thread)

        path_test = os.getcwd()
        thread = threading.Thread(target=callback)
        thread.start()
        self.__threads.append(thread)

    def stopExplainerDashboard(self):
        print("Needs to be implemented!")
        # kill thread



