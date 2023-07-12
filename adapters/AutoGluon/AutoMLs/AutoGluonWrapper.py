import numpy as np

class AutoGluonWrapper:

    def __init__(self, model) -> None:
        self.__model = model

    def predict(self, x, **kwargs):
        self.__model.predict(x=x, **kwargs)

    def predict_proba(self, x, **kwargs):

        probabilities_raw = self.__model.predict_proba(x, **kwargs)
        probabilities = np.array(probabilities_raw)
        return probabilities
