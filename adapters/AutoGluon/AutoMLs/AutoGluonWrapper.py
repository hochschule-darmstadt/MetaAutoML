import numpy as np
from BaseWrapper import BaseWrapper

class AutoGluonWrapper(BaseWrapper):

    def __init__(self, model, config) -> None:
        super().__init__(model, config)

    def predict(self, X, **kwargs):
        X_predict = self._prepare_dataset(X)
        return self._model.predict(X_predict)

    def predict_proba(self, X, **kwargs):
        X_predict = self._prepare_dataset(X)

        probabilities_raw = self._model.predict_proba(X_predict, **kwargs)
        probabilities = np.array(probabilities_raw)
        return probabilities
