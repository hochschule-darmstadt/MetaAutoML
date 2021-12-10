import tensorflow as tf
import numpy as np
import pandas as pd

import autokeras as ak
from tensorflow.keras.models import load_model

if __name__ == '__main__':
	x_to_predict = pd.read_csv(#REPLAVE WITH PATH TO PREDICTION CSV, quotechar='"', skipinitialspace=True)
	x_to_predict_numpy = x_to_predict.to_numpy()
	loaded_model = load_model("model_autokeras", custom_objects=ak.CUSTOM_OBJECTS)

	predicted_y = loaded_model.predict(tf.expand_dims(x_to_predict_numpy.astype(np.unicode), -1))
	predicted_y[predicted_y < 0.5] = 0
	predicted_y[predicted_y > 0.5] = 1
	print(predicted_y)