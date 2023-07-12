import numpy as np

class LAMAWrapper:

    def __init__(self, model) -> None:
        self.__model = model

    def predict(self, x, **kwargs):
        predictions = self.__model.predict(x=x, **kwargs)
        if self.__model.task.name == "multiclass":
            ind =  np.argmax(predictions.data, axis=1)
            inverse_class_mapping = {y: x for x,y in self.__model.reader.class_mapping.items()}
            labels = [inverse_class_mapping[i] for i in range(len(inverse_class_mapping))]
            ind = list(map(inverse_class_mapping.get, ind))
            predicted_y = np.reshape(ind, (-1, 1))
        else:
            predicted_y = (np.array(predicted_y.data) >= 0.5).astype(int)
            predicted_y = np.concatenate(predicted_y)
        return predicted_y

    def predict_proba(self, x, **kwargs):

        probabilities_raw = self.__model.predict(x, **kwargs)
        probabilities = np.array(probabilities_raw.data)
        if self.__model.task.name == "binary":
            diff = 1 - probabilities
            probabilities = np.concatenate((probabilities, diff), axis=1)
        return probabilities
