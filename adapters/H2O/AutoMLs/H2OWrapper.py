
import numpy as np
import h2o
import os

from BaseWrapper import BaseWrapper

class H2OWrapper(BaseWrapper):
    """
    h2o models can not be exported as a binary and it is set to None for export.
    Therefore the model is loaded with self.load_model(). The path has to be in the configuration.
    """
    def __init__(self, model, config) -> None:
        super().__init__(model, config)

    def predict(self, X, **kwargs):
        X_predict = self._prepare_dataset(X.copy())

        return self._model.predict(h2o.H2OFrame(X_predict))

    def predict_proba(self, X, **kwargs):
        X_predict = self._prepare_dataset(X.copy())

        model = self._model

        h2o_probabilities = model.predict(h2o.H2OFrame(X_predict), **kwargs)

        h2o_predictions_df = h2o_probabilities.as_data_frame(use_pandas=True)

        if len(h2o_predictions_df.columns) > 2:
                    # Wir ignorieren die erste Spalte, die die Klasse enthaelt
                    probabilities_df = h2o_predictions_df.iloc[:, 1:]

        return probabilities_df.to_numpy()

    def load_model(self) -> None:
        """Load the model for the wrapper from disk
        only implemented for h2o
        """
        h2o.init()
        self._model = h2o.load_model(os.path.join(self._config["result_folder_location"], 'model_h2o.p'))
