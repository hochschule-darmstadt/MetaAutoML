import os
import dill
from typing import Tuple
import pandas as pd
from AdapterTabularUtils import *

class BaseWrapper:

    def __init__(self, model, config) -> None:
        self._model = model
        self._config = config
        self._pca_transformer, self._perform_pca = self._load_pca_model(self._config["dataset_configuration"], self._config["result_folder_location"])

    def predict(self, X, **kwargs):
        return NotImplemented

    def predict_proba(self, X, **kwargs):
        return NotImplemented

    def _prepare_dataset(self, X):
        #hopefully next release of explainer dashboard will fix this, else leave the copy or this will break the dashbaord as the change will manipulate the data in explainer dashboard
        X_predict = X.copy()
        X_predict, y = prepare_tabular_dataset(X_predict, self._config, True)
        if self._perform_pca == True:
            X_predict = self.apply_pca_feature_extraction(X_predict, self._config["dataset_configuration"])
        return X_predict

    def _load_pca_model(self, features: dict, result_folder):
        perform_pca = False
        pca_transformer = {}

        for key, value in features["schema"].items():
            try:
                if value['preprocessing']['pca'] == True and value['role_selected'] != ':target':
                    perform_pca = True
                    break
            except:
                pass

        if perform_pca == False:
            return None, perform_pca

        with open(os.path.join(result_folder, 'pca_model.dill'), 'rb') as file:
            pca_transformer = dill.load(file)

        return pca_transformer, perform_pca

    def apply_pca_feature_extraction(self, X: pd.DataFrame, features: dict) -> Tuple[pd.DataFrame, pd.Series]:
        pca_features = []

        for key, value in features["schema"].items():
            try:
                if value['preprocessing']['pca'] == True and value['role_selected'] != ':target':
                    pca_features.append(key)
            except:
                pass

        if len(pca_features) == 0:
            return X

        df_no_pca = X.drop(pca_features, axis=1)
        df_pca = X[pca_features]

        categorical_columns = df_pca.select_dtypes(include=['object']).columns
        numeric_columns = df_pca.select_dtypes(include=['float64', 'int64']).columns

        numeric_data = df_pca[numeric_columns]
        numeric_data = numeric_data.fillna(numeric_data.mean()).values

        scaled_numeric_data = self._pca_transformer["scaler"].transform(numeric_data)

        transformed_features = self._pca_transformer["pca"].transform(scaled_numeric_data)

        transformed_data = pd.DataFrame(
            data=transformed_features,
            columns=[f"PC{i}" for i in range(1, self._pca_transformer["pca"].n_components_ + 1)]
        )

        data = pd.concat([pd.DataFrame(transformed_data).set_index(df_pca.index), pd.DataFrame(df_pca[categorical_columns])], axis=1)

        df_no_pca_copy = df_no_pca
        df_merged = pd.concat([data, df_no_pca], axis=1)
        return df_merged
