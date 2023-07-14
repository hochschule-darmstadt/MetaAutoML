import numpy as np
from BaseWrapper import BaseWrapper

class LAMAWrapper(BaseWrapper):

    def __init__(self, model, config) -> None:
        super().__init__(model, config)

    def predict(self, X, **kwargs):
        X_predict = self._prepare_dataset(X)

        predictions = self._model.predict(x=X_predict, **kwargs)
        if self._model.task.name == "multiclass":
            ind =  np.argmax(predictions.data, axis=1)
            inverse_class_mapping = {y: x for x,y in self._model.reader.class_mapping.items()}
            labels = [inverse_class_mapping[i] for i in range(len(inverse_class_mapping))]
            ind = list(map(inverse_class_mapping.get, ind))
            predicted_y = np.reshape(ind, (-1, 1))
        else:
            predicted_y = (np.array(predicted_y.data) >= 0.5).astype(int)
            predicted_y = np.concatenate(predicted_y)
        return predicted_y

    def predict_proba(self, X, **kwargs):
        X_predict = self._prepare_dataset(X)

        probabilities_raw = self._model.predict(X_predict, **kwargs)
        probabilities = np.array(probabilities_raw.data)
        if self._model.task.name == "binary":
            diff = 1 - probabilities
            probabilities = np.concatenate((probabilities, diff), axis=1)
        return probabilities
