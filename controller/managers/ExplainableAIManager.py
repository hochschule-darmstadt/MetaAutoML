import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import threading
import sys
import numpy as np

from AdapterManager import AdapterManager
from Controller_bgrpc import *


def make_html_force_plot(base_value, shap_values, X, path, filename_detail):
    import shap
    shap.initjs()
    filename = os.path.join(path, f"shap_force_plot_{filename_detail}.html")
    shap.save_html(filename, shap.force_plot(base_value, shap_values, X))
    return filename


def make_svg_waterfall_plot(base_value, shap_values, X, path, filename_detail):
    import shap
    filename = os.path.join(path, f"waterfall_{filename_detail}.svg")
    plot = shap.waterfall_plot(
        shap.Explanation(values=shap_values, base_values=base_value,
                         data=X, feature_names=X.index.tolist()),
        max_display=50,
        show=False)
    plot.savefig(filename)
    plt.clf()
    return filename


def make_svg_beeswarm_plot(base_value, shap_values, X, path, filename_detail):
    import shap
    filename = os.path.join(path, f"beeswarm_{filename_detail}.svg")
    shap.plots.beeswarm(shap.Explanation(values=shap_values,
                                         base_values=base_value,
                                         data=X,
                                         feature_names=X.columns.tolist()),
                        show=False)
    plt.savefig(filename)
    plt.clf()
    return filename


def make_svg_summary_plot(shap_values, X, path):
    import shap
    filename = os.path.join(path, "summary_bar.svg")
    shap.summary_plot(shap_values=shap_values, features=X, plot_type='bar', show=False)
    plt.savefig(filename)
    plt.clf()
    return filename


def compile_html(plots, path):
    path = os.path.join(path, "explanation.html")
    with open(path, "w", encoding="UTF-8") as output_file:
        output_file.write(f"<h1> SHAP output </h1>\n\n")
        for filename in plots:
            with open(filename, "r", encoding="UTF-8") as shap_file:
                output_file.write(f"<h1> {filename} </h1>\n\n")
                output_file.write(shap_file.read())
                output_file.write("\n\n")
                shap_file.close()
        output_file.close()


def plot_tabular_classification(dataset_X, dataset_Y, predictions, explainer, shap_values, plot_path):
    plot_filenames = []
    dataset_X[dataset_X.select_dtypes(['bool']).columns] = dataset_X[dataset_X.select_dtypes(['bool']).columns].astype(str)
    classlist = list(val for val in dataset_Y.unique())
    # TODO: Remove debug
    print(f"[ExplainableAIManager]: classlist is: {classlist}")
    print(f"[ExplainableAIManager]: distinct dataset Y is: {dataset_Y.unique()}")
    print(f"[ExplainableAIManager]: predictions[0:10] is : {predictions[0:10]}")
    for class_idx, class_value in enumerate(classlist):
        print(f"[ExplainableAIManager]: class_idx is: {class_idx} | class_value is {class_value}")
        row_idx = int(dataset_Y[dataset_Y == class_value].index[0])
        # Locate prediction (class_idx is the true value)
        print(f"[ExplainableAIManager]: row_idx is : {row_idx}")
        print(f"[ExplainableAIManager]: predictions[row_idx] is : {predictions[row_idx]}")
        prediction_class_idx = classlist.index(predictions[row_idx])

        filename = make_html_force_plot(base_value=explainer.expected_value[class_idx],
                                        shap_values=shap_values[class_idx][row_idx], X=dataset_X.iloc[row_idx],
                                        path=plot_path,
                                        filename_detail=f"classification_rowidx{row_idx}_classidx{class_idx}_truth")
        plot_filenames.append(filename)
        filename = make_html_force_plot(base_value=explainer.expected_value[int(prediction_class_idx)],
                                        shap_values=shap_values[int(prediction_class_idx)][row_idx], X=dataset_X.iloc[row_idx],
                                        path=plot_path,
                                        filename_detail=f"classification_rowidx{row_idx}_classidx{int(prediction_class_idx)}_prediction")
        plot_filenames.append(filename)

        filename = make_svg_waterfall_plot(base_value=explainer.expected_value[class_idx],
                                           shap_values=shap_values[class_idx][row_idx], X=dataset_X.iloc[row_idx],
                                           path=plot_path,
                                           filename_detail=f"classification_rowidx{row_idx}_classidx{class_idx}_truth")
        plot_filenames.append(filename)
        filename = make_svg_waterfall_plot(base_value=explainer.expected_value[int(prediction_class_idx)],
                                           shap_values=shap_values[int(prediction_class_idx)][row_idx], X=dataset_X.iloc[row_idx],
                                           path=plot_path,
                                           filename_detail=f"classification_rowidx{row_idx}_classidx{int(prediction_class_idx)}_prediction")
        plot_filenames.append(filename)
        filename = make_svg_beeswarm_plot(base_value=explainer.expected_value[class_idx],
                                          shap_values=shap_values[class_idx], X=dataset_X, path=plot_path,
                                          filename_detail=f"classification_classidx{class_idx}_truth")
        plot_filenames.append(filename)
        filename = make_svg_beeswarm_plot(base_value=explainer.expected_value[int(prediction_class_idx)],
                                          shap_values=shap_values[int(prediction_class_idx)], X=dataset_X, path=plot_path,
                                          filename_detail=f"classification_classidx{class_idx}_prediction")
        plot_filenames.append(filename)
        filename = make_svg_summary_plot(shap_values, dataset_X, plot_path)
        plot_filenames.append(filename)
    return plot_filenames


def feature_preparation(X, features):
    for column, dt in features:
        if DataType(dt) is DataType.DATATYPE_IGNORE:
            X.drop(column, axis=1, inplace=True)
        elif DataType(dt) is DataType.DATATYPE_CATEGORY:
            X[column] = X[column].astype('category')
        elif DataType(dt) is DataType.DATATYPE_BOOLEAN:
            X[column] = X[column].astype('bool')
        elif DataType(dt) is DataType.DATATYPE_INT:
            X[column] = X[column].astype('int')
        elif DataType(dt) is DataType.DATATYPE_FLOAT:
            X[column] = X[column].astype('float')
    return X


class ExplainableAIManager:
    def __init__(self, data_storage):
        self.__data_storage = data_storage
        self.__adapterManager = AdapterManager(self.__data_storage)
        self.__threads = []

    def explain(self, username, model_id):
        def callback(thread, username, model, status, detail, plot_paths):
            with self.__data_storage.Lock():
                # Add explanation results to model
                model_data = {"explanation": {"status": status, "detail": detail, "plot_paths": plot_paths}}
                self.__data_storage.UpdateModel(username, str(model['_id']), model_data)

                # Add explanation results (status) to training
                training = self.__data_storage.GetTraining(username, model['training_id'])
                if "explanation" in training:
                    training["explanation"].update({model['automl_name']: status})
                else:
                    training["explanation"] = {model['automl_name']: status}
                self.__data_storage.UpdateTraining(username, model['training_id'], {"explanation": training["explanation"]})

            # Remove tread from thread list
            self.__threads.remove(thread)

        # Create a new thread for the explanation
        thread = threading.Thread(target=self.explain_shap, name=f"{username}:{model_id}", args=(username, model_id, callback))
        thread.start()
        self.__threads.append(thread)
        self.__data_storage.UpdateModel(username, model_id, {"explanation": {"status": "started"}})
        return
    
    def explain_shap(self, username, model_id, callback, number_of_samples=5):
        import shap
        model = self.__data_storage.GetModel(username, model_id)
        config = self.__data_storage.GetTraining(username, model["training_id"])
        dataset_path = self.__data_storage.GetDataset(username, config["dataset_id"])[1]["path"]

        print(f"[ExplainableAIManager]: Initializing new shap explanation. AutoML: {model['automl_name'].replace(':', '')} | Training ID: {model['training_id']} | Dataset: {config['dataset_id']} ({config['dataset_name']})")
        
        config["file_location"], config["file_name"] = os.path.split(dataset_path)
        output_path = os.path.join(os.getcwd(), "app-data", "training", model["automl_name"].replace(":", ""), username, model["training_id"], "result", "plots")
        os.makedirs(output_path, exist_ok=True)
        plot_path = os.path.join(output_path, "plots")
        os.makedirs(plot_path, exist_ok=True)
        plot_filenames = []
        
        dataset = pd.read_csv(dataset_path)
        dataset = feature_preparation(dataset, config["dataset_configuration"]["features"].items())
        dataset_X = dataset.drop(config["configuration"]["target"]["target"], axis=1)
        dataset_Y = dataset[config["configuration"]["target"]["target"]]
        sampled_dataset_X = dataset_X.iloc[0:number_of_samples, :]

        print(f"[ExplainableAIManager]: Output is saved to {output_path}")
        print(f"[ExplainableAIManager]: Starting explanation with {number_of_samples} samples. This may take a while.")

        if config["task"] == ":tabular_classification":
            try:
                explainer = self.get_shap_explainer(username, model, config, sampled_dataset_X)
            except RuntimeError as e:
                callback(thread=threading.current_thread(), username=username, model=model, status="failed", detail=f"exeption: {e}", plot_paths=[])
                return
            shap_values = explainer.shap_values(sampled_dataset_X)

            predictions = self.get_predictions(username, model_id, dataset_path, model, config, dataset_Y)

            print("[ExplainableAIManager]: Explanation finished. Beginning plots.")

            filenames = plot_tabular_classification(sampled_dataset_X, dataset_Y, predictions, explainer, shap_values, plot_path)
            plot_filenames = filenames
        else:
            message = "The ML task of the selected training is not tabular classification. This module is only compatible with tabular classification."
            print("[ExplainableAIManager]:" + message)
            callback(thread=threading.current_thread(), username=username, model=model, status="failed", detail=f"incompatible: {message}", plot_paths=[])
            return

        compile_html(plot_filenames, output_path)
        print(f"[ExplainableAIManager]: Plots for {model['automl_name']} completed")
        callback(thread=threading.current_thread(), username=username, model=model, status="finished", detail=f"{len(plot_filenames)} plots created", plot_paths=plot_filenames)

    def get_shap_explainer(self, username, model, config, sampled_dataset_x):
        """
        Calculate and return the SHAP explainer object.
        Usually this is a one-liner as with any "normal" ML-model the explainer is passed the model predict_proba (for
        classification tasks) function.
        But as here this function is called over gRPC, and it is implemented by AutoML's just passing the functions will
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
                result = self.__adapterManager.explain_automl(json.dumps(chunk.tolist()),
                                                              username,
                                                              model["automl_name"],
                                                              model["training_id"],
                                                              config)
                if result is None:
                    raise RuntimeError(f"Unable to create SHAP values for Automl {model['automl_name']} | Training_id {model['training_id']}")
                else:
                    probabilities = probabilities + json.loads(result.probabilities)

            return pd.DataFrame(probabilities)

        import shap
        return shap.KernelExplainer(prediction_probability, sampled_dataset_x)

    def get_predictions(self, username, model_id, dataset_path, model, config, dataset_Y):
        """
        Get and process predictions.
        Predictions are acquired using the TestAutoml() functionality.
        After the predictions are made they are processed and returned.

        Some AutoMLs do not return the same datatype in their predictions compared to the truth (dataset_Y)
        Therefore it is necessary to test and possibly convert the predictions before they can be processed further.
        """
        request = TestAutoMlRequest
        request.username = username
        request.model_id = model_id

        with open(dataset_path, "r") as f:
            request.test_data = f.read().encode()
        predictions = list(self.__adapterManager.TestAutoml(request,
                                                            model["automl_name"],
                                                            model["training_id"],
                                                            config).predictions)

        # Convert mismatched datatypes between the dataset_Y and the list of predictions
        print(f"[ExplainableAIManager]: Predictions: "
              f"dataset_Y.iloc[0] is {dataset_Y.iloc[0]} with dtype {dataset_Y.iloc[0]}"
              f"predictions[0] is {predictions[0]} with dtype {type(predictions[0])}")
        if dataset_Y.dtype == "bool" and type(predictions[0]) == str:
            # if predictions are string and truth is bool the predictions could be either '0' or 'False'
            try:  # try to convert a string formatted int
                return [bool(int(pred)) for pred in predictions]
            except ValueError as e:
                pass
            try:  # try to convert a string formatted bool
                return [bool(pred) for pred in predictions]
            except ValueError as e:
                pass
        if dataset_Y.dtype == "bool" and type(predictions[0]) == int:
            return [bool(pred) for pred in predictions]
        return predictions


