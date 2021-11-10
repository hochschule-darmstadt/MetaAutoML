import tensorflow as tf
import numpy as np
import pandas as pd
import sys
import autokeras as ak
from tensorflow.keras.models import load_model

if __name__ == '__main__':
    filepath = sys.argv[1]
    x_to_predict = pd.read_csv(filepath, quotechar='"', skipinitialspace=True)
    x_to_predict_numpy = x_to_predict.to_numpy()
    loaded_model = load_model("model_autokeras", custom_objects=ak.CUSTOM_OBJECTS)

    predicted_y = loaded_model.predict(tf.expand_dims(x_to_predict_numpy.astype(np.unicode), -1))

    print(predicted_y)