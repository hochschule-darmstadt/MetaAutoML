
import numpy as np
import h2o
import os

from BaseWrapper import BaseWrapper

class H2OWrapper(BaseWrapper):

    def __init__(self, model, config) -> None:
        super().__init__(model, config)

    def predict(self, X, **kwargs):
        X_predict = self._prepare_dataset(X.copy())

        return self._model.predict(h2o.H2OFrame(X_predict))

    def predict_proba(self, X, **kwargs):
        X_predict = self._prepare_dataset(X.copy())

        #self._check_data_format((X_predict, None), predict=True)
        # dataset = self._adapt(X_predict, self._model.inputs, 32)
        # pipeline = self._model.tuner.get_best_pipeline()
        model = self._model
        # dataset = pipeline.transform_x(dataset)
        # dataset = tf.data.Dataset.zip((dataset, dataset))
        probabilities = model.predict(h2o.H2OFrame(X_predict), **kwargs)
        # H2o does not provide a predict_proba() function to get the class probabilities.
        # Instead, it returns these probabilities (in case there is a binary classification) when calling predict
        # but only as a one dimensional array. Shap however requires the probabilities in the format
        # [[prob class 0, prob class 1], [...]]. So to return the proper format we have to process the results of
        # predict().
        if probabilities.shape[1] == 1:
            probabilities = np.array([np.array([1 - prob[0], prob[0]]) for prob in probabilities.tolist()])
        return probabilities

    def load_model(self) -> None:
        h2o.init()
        self._model = h2o.load_model(os.path.join(self._config["result_folder_location"], 'model_h2o.p'))
