import tensorflow as tf
import numpy as np
import pandas as pd
import autokeras as ak
import os
import sys
import io
from tensorflow.keras.models import load_model

if __name__ == '__main__':
	x_to_predict = pd.read_csv("C:/Users/hda10126/Desktop/titanic-dataset/titanic_test.csv", quotechar='"', skipinitialspace=True)
	x_to_predict_numpy = x_to_predict.to_numpy()
	clf = ak.StructuredDataClassifier(overwrite=True, max_trials=3, seed=42)
	clf.fit("C:/Users/hda10126/Desktop/Ontology based Meta Auto Machine Learning/Controller/managers/datasets/titanic_train.csv", "survived", epochs=10)
	result = clf.predict(x_to_predict_numpy.astype(np.unicode))
	#print(result)
	model = clf.export_model()
	model.summary()
	model.save("model_autokeras", save_format="tf")
	loaded_model = load_model("model_autokeras", custom_objects=ak.CUSTOM_OBJECTS)
	loaded_model.summary()
	BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	#for root, dirs, files in os.walk(BASE_DIR, topdown = False):
	#	for name in files:
			#print(os.path.join(root, name))

	predicted_y = loaded_model.predict(x_to_predict_numpy.astype(np.unicode))
	predicted_y[predicted_y < 0.5] = 0
	predicted_y[predicted_y > 0.5] = 1