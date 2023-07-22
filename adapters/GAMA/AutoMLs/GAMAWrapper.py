from sklearn.base import BaseEstimator, ClassifierMixin #Need or else dashboard will thing no predict_proba exists, only an issue with evalml and gama
from BaseWrapper import BaseWrapper
import numpy as np

class GAMAWrapper(BaseEstimator, ClassifierMixin, BaseWrapper):

    def __init__(self, model, config) -> None:
        super().__init__(model, config)

    def predict(self, X, **kwargs):
        X_predict = self._prepare_dataset(X.copy())
        predictions_raw = self._model.predict(X_predict)
        predictions = np.array(predictions_raw)
        return predictions

    def predict_proba(self, X, **kwargs):
        X_predict = self._prepare_dataset(X.copy())
        probabilities_raw = self._model.predict_proba(X_predict).tolist()
        probabilities = np.array(probabilities_raw)
        return probabilities
