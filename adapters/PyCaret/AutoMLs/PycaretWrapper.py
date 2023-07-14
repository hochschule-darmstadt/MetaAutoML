import numpy as np
from BaseWrapper import BaseWrapper

class PycaretWrapper(BaseWrapper):

    def __init__(self, model, config) -> None:
        super().__init__(model, config)

    def predict(self, X, **kwargs):
        X_predict = self._prepare_dataset(X)

        return self._model.predict(x=X_predict, **kwargs)

    def predict_proba(self, X, **kwargs):
        X_predict = self._prepare_dataset(X)

        return self._model.predict_proba(X_predict, **kwargs)
