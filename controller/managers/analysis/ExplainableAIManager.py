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
    def __init__(self, data_storage: DataStorage, adapter_manager: AdapterManager, explainable_lock: ThreadLock):
        self.__data_storage = data_storage
        self.__adapter_manager = adapter_manager
        self.__threads = []
        self.__explainable_lock = explainable_lock

    def explain(self, user_id, model_id):
        """
        Start new explanation.
        This spawns a separate thread which is saved in self.__threads and is removed upon completion.
        After the thread is finished (or has crashed) the database is updated with the new information.
        """
        def callback(thread, user_id, model, status, detail, plots, title):
            with self.__data_storage.lock():
                # Add explanation results to model
                model_data = {"explanation":
                                  {"status": status,
                                   "detail": detail,
                                   "content": [{"title": title, "items": plots}]}}
                self.__data_storage.update_model(user_id, str(model['_id']), model_data)

                # Add explanation results (only the status) to training
                found, training = self.__data_storage.get_training(user_id, model['training_id'])
                if "explanation" in training:
                    training["explanation"].update({model['auto_ml_solution']: status})
                else:
                    training["explanation"] = {model['auto_ml_solution']: status}
                self.__data_storage.update_training(user_id, model['training_id'], {"explanation": training["explanation"]})

            # Remove tread from thread list
            self.__threads.remove(thread)

        # Create a new thread for the explanation
        thread = threading.Thread(target=self.explain_shap, name=f"{user_id}:{model_id}", args=(user_id, model_id, callback))
        thread.start()
        self.__threads.append(thread)
        self.__data_storage.update_model(user_id, model_id, {"explanation": {"status": "started"}})
        return



    def explain_shap(self, user_id, model_id, callback, number_of_samples=25):
        found, model = self.__data_storage.get_model(user_id, model_id)
        found, training = self.__data_storage.get_training(user_id, model["training_id"])
        dataset_path = self.__data_storage.get_dataset(user_id, training["dataset_id"])[1]["path"]

        print(f"[ExplainableAIManager]: Initializing new shap explanation. AutoML: {model['auto_ml_solution'].replace(':', '')} | Training ID: {model['training_id']} | Dataset: {training['dataset_id']}")

        training["file_location"], training["file_name"] = os.path.split(dataset_path)
        output_path = os.path.join(os.getcwd(), "app-data", "training", model["auto_ml_solution"].replace(":", ""), user_id, training["dataset_id"], model["training_id"], "result")
        os.makedirs(output_path, exist_ok=True)
        plot_path = os.path.join(output_path, "plots")
        os.makedirs(plot_path, exist_ok=True)

        dataset = CsvManager.read_dataset(dataset_path, training["dataset_configuration"]['file_configuration'], training["dataset_configuration"]['schema'])
        dataset_X, dataset_Y = feature_preparation(dataset, training["dataset_configuration"]["schema"].items(), training["dataset_configuration"]["file_configuration"]["datetime_format"])

        createExplainerDashboard(model, dataset_X, dataset_Y)

        sampled_dataset_X = dataset_X.iloc[0:number_of_samples, :]

        print(f"[ExplainableAIManager]: Output is saved to {output_path}")
        print(f"[ExplainableAIManager]: Starting explanation with {number_of_samples} samples. This may take a while.")

        if training["configuration"]["task"] == ":tabular_classification":
            try:
                explainer = self.get_shap_explainer(user_id, model, training, sampled_dataset_X)
            except RuntimeError as e:
                callback(thread=threading.current_thread(), user_id=user_id, model=model, status="failed", detail=f"exeption: {e}", plots=[], title="SHAP Explanation")
                return
            shap_values = explainer.shap_values(sampled_dataset_X)

            print("[ExplainableAIManager]: Explanation finished. Beginning plots.")
            with self.__explainable_lock.lock():
                print("[ExplainableAIManager]: ENTERING LOCK.")
                plots = plot_tabular_classification(sampled_dataset_X,
                                                            dataset_Y,
                                                            dataset_Y.name,
                                                            number_of_samples,
                                                            explainer,
                                                            shap_values,
                                                            plot_path)
                print("[ExplainableAIManager]: EXITING LOCK.")
        else:
            message = "The ML task of the selected training is not tabular classification. This module is only compatible with tabular classification."
            print("[ExplainableAIManager]:" + message)
            callback(thread=threading.current_thread(), user_id=user_id, model=model, status="failed", detail=f"incompatible: {message}", plots=[], title="SHAP Explanation")
            return

        print(f"[ExplainableAIManager]: Plots for {model['auto_ml_solution']} completed")
        callback(thread=threading.current_thread(), user_id=user_id, model=model, status="finished", detail=f"{len(plots)} plots created", plots=plots, title="SHAP Explanation")

    def get_shap_explainer(self, user_id, model, config, sampled_dataset_x):
        """
        Calculate and return the SHAP explainer object.
        Usually this is a one-liner as with any "normal" ML-model the explainer is passed the model predict_proba (for
        classification tasks) function.
        But as here this function is called over gRPC, and it is implemented by AutoMLs, just passing the functions will
        not work at all.
        Our new prediction_probability function does several things (on this side and on the adapter side):
            - Pass the data requested by SHAP to the adapter and return the probabilities (both sides)
            - Convert the data back to the original Dataframe format (concerning columns and datatypes) while keeping
                the content requested by SHAP (adapter side)
            - Chunk the data if the requested data size is too large (this side). This is because gRPC is limited to a
                certain file size but SHAP (especially with larger sample sizes) often requests very large datasets.
                If the dataset as a whole is too large it gets requested as several chunks.
            - Convert the received data back into a dataframe so that SHAP can work with the results.
        """
        def prediction_probability(data):
            # Get number of chunks necessary. The max gRPC msg. size is 4194304.
            no_chunks = int(sys.getsizeof(json.dumps(data.tolist())) / 4190000) + 1
            data_chunks = np.array_split(np.array(data), no_chunks)
            probabilities = []
            for chunk in data_chunks:
                # Request the data
                result = self.__adapter_manager.explain_model(json.dumps(chunk.tolist()))
                if result is None:
                    raise RuntimeError(f"Unable to create SHAP values for Automl {model['auto_ml_solution']} | Training_id {model['training_id']}")
                else:
                    probabilities = probabilities + json.loads(result.probabilities)

            return pd.DataFrame(probabilities)
        import shap
        return shap.KernelExplainer(prediction_probability, sampled_dataset_x)
    
def createExplainerDashboard(model, x_test, y_test):
    dashboard = ExplainerDashboard(ClassifierExplainer(model, x_test, y_test))
    dashboard.save_html("./binary_dashboard.html")
    dashboard.explainer.dump("./binary_dashboard.dill")
    runExplainerDashboard()

def runExplainerDashboard():
    dashboard = ExplainerDashboard(ClassifierExplainer.from_file("./binary_dashboard.dill"))
    dashboard.run(8045)



