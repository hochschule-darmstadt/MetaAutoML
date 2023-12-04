# import tensorflow as tf
# from tensorflow import nest
# from autokeras.utils import data_utils
import numpy as np
from BaseWrapper import BaseWrapper

class AutoKerasWrapper(BaseWrapper):

    def __init__(self, model, config) -> None:
        super().__init__(model, config)

    def predict(self, X, **kwargs):
        X_predict = self._prepare_dataset(X.copy())

        return self._model.predict(X_predict)

    def predict_proba(self, X, **kwargs):
        X_predict = self._prepare_dataset(X.copy())

        self._check_data_format((X_predict, None), predict=True)
        dataset = self._adapt(X_predict, self._model.inputs, 32)
        pipeline = self._model.tuner.get_best_pipeline()
        model = self._model.tuner.get_best_model()
        dataset = pipeline.transform_x(dataset)
        dataset = tf.data.Dataset.zip((dataset, dataset))
        probabilities = model.predict(dataset, **kwargs)
        # Keras is strange as it does not provide a predict_proba() function to get the class probabilities.
        # Instead, it returns these probabilities (in case there is a binary classification) when calling predict
        # but only as a one dimensional array. Shap however requires the probabilities in the format
        # [[prob class 0, prob class 1], [...]]. So to return the proper format we have to process the results of
        # predict().
        if probabilities.shape[1] == 1:
            probabilities = np.array([np.array([1 - prob[0], prob[0]]) for prob in probabilities.tolist()])
        return probabilities

    def _adapt(self, dataset, hms, batch_size):
        if isinstance(dataset, tf.data.Dataset):
            sources = data_utils.unzip_dataset(dataset)
        else:
            sources = nest.flatten(dataset)
        adapted = []
        for source, hm in zip(sources, hms):
            source = hm.get_adapter().adapt(source, batch_size)
            adapted.append(source)
        if len(adapted) == 1:
            return adapted[0]
        return tf.data.Dataset.zip(tuple(adapted))

    def _check_data_format(self, dataset, validation=False, predict=False):
        """Check if the dataset has the same number of IOs with the model."""
        if validation:
            in_val = " in validation_data"
            if isinstance(dataset, tf.data.Dataset):
                x = dataset
                y = None
            else:
                x, y = dataset
        else:
            in_val = ""
            x, y = dataset

        if isinstance(x, tf.data.Dataset) and y is not None:
            raise ValueError(
                "Expected y to be None when x is "
                "tf.data.Dataset{in_val}.".format(in_val=in_val)
            )

        if isinstance(x, tf.data.Dataset):
            if not predict:
                x_shapes, y_shapes = data_utils.dataset_shape(x)
                x_shapes = nest.flatten(x_shapes)
                y_shapes = nest.flatten(y_shapes)
            else:
                x_shapes = nest.flatten(data_utils.dataset_shape(x))
        else:
            x_shapes = [a.shape for a in nest.flatten(x)]
            if not predict:
                y_shapes = [a.shape for a in nest.flatten(y)]

        if len(x_shapes) != len(self._model.inputs):
            raise ValueError(
                "Expected x{in_val} to have {input_num} arrays, "
                "but got {data_num}".format(
                    in_val=in_val, input_num=len(self._model.inputs), data_num=len(x_shapes)
                )
            )
        if not predict and len(y_shapes) != len(self._model.outputs):
            raise ValueError(
                "Expected y{in_val} to have {output_num} arrays, "
                "but got {data_num}".format(
                    in_val=in_val,
                    output_num=len(self._model.outputs),
                    data_num=len(y_shapes),
                )
            )
