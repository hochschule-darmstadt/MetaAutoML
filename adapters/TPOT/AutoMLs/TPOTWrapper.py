import numpy as np
from BaseWrapper import BaseWrapper

class TPOTWrapper(BaseWrapper):

    def __init__(self, model, config) -> None:
        super().__init__(model, config)

    def predict(self, X, **kwargs):
        X_predict = self._prepare_dataset(X)

        return self._model.predict(X_predict)

    def predict_proba(self, X, **kwargs):
        X_predict = self._prepare_dataset(X)

        return self._model.predict_proba(X_predict, **kwargs)
