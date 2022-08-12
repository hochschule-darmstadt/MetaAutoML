import json
import logging
import shap
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, datetime

from AdapterManager import AdapterManager
from Controller_bgrpc import *


def make_html_force_plot(base_value, shap_values, X, path, filename_detail):
    shap.initjs()
    filename = os.path.join(path, f"shap_force_plot_{filename_detail}.html")
    shap.save_html(filename, shap.force_plot(base_value, shap_values, X))
    return filename


def make_svg_waterfall_plot(base_value, shap_values, X, path, filename_detail):
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
    classlist = list(str(val) for val in dataset_Y.unique())
    for class_idx, class_value in enumerate(classlist):
        row_idx = dataset_Y[dataset_Y.astype(str) == class_value].index[0]
        # Locate prediction (class_idx is the true value)
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
        logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
    
    def explain_shap(self, request: TestAutoMlRequest, number_of_samples=5):
        model = self.__data_storage.GetModel(request.username, request.model_id)
        config = self.__data_storage.GetTraining(request.username, model["training_id"])
        dataset_path = self.__data_storage.GetDataset(request.username, config["dataset_id"])[1]["path"]

        logging.info(f"Initializing new shap explanation. AutoML: {model['automl_name'].replace(':', '')} | Training ID: {model['training_id']} | Dataset: {config['dataset_id']} ({config['dataset_name']})")
        
        config["file_location"], config["file_name"] = os.path.split(dataset_path)
        output_path = os.path.join(os.getcwd(), "app-data", "output", model["automl_name"].replace(":", ""), model["training_id"])
        os.makedirs(output_path, exist_ok=True)
        plot_path = os.path.join(output_path, "plots")
        os.makedirs(plot_path, exist_ok=True)
        plot_filenames = []
        
        dataset = pd.read_csv(dataset_path)
        dataset = feature_preparation(dataset, config["dataset_configuration"]["features"].items())
        dataset_X = dataset.drop(config["configuration"]["target"]["target"], axis=1)
        dataset_Y = dataset[config["configuration"]["target"]["target"]]
        sampled_dataset_X = dataset_X.iloc[0:number_of_samples, :]

        logging.info(f"Output is saved to {output_path}")
        logging.info(f"Starting explanation with {number_of_samples} samples. This may take a while.")

        if config["task"] == ":tabular_classification":
            explainer = self.get_shap_explainer(request, model, config, sampled_dataset_X)
            shap_values = explainer.shap_values(sampled_dataset_X)

            with open(dataset_path, "r") as f:
                request.test_data = f.read().encode()
            predictions = list(self.__adapterManager.TestAutoml(request, model["automl_name"],
                                                                model["training_id"],
                                                                config).predictions)

            logging.info("Explanation finished. Beginning plots.")

            filenames = plot_tabular_classification(sampled_dataset_X, dataset_Y, predictions, explainer, shap_values, plot_path)
            plot_filenames = filenames
        else:
            logging.warning("The ML task of the selected training is not tabular classification. This module is only compatible with tabular classification.")
            return

        compile_html(plot_filenames, output_path)
        logging.info("Plots completed")

    def get_shap_explainer(self, request, model, config, sampled_dataset_X):
        def prediction_probability(data):
            request.test_data = data.tolist()
            result = self.__adapterManager.explain_automl(request, model["automl_name"],
                                                          model["training_id"],
                                                          config)
            if result is None:
                raise RuntimeError("Unable to create SHAP values")
            else:
                return pd.DataFrame(json.loads(result.probabilities))

        return shap.KernelExplainer(prediction_probability, sampled_dataset_X)
