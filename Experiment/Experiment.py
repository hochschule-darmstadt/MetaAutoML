
#import tensorflow as tf
#import numpy as np
#import pandas as pd
#import autokeras as ak
#import os
import sys
#import io

#from threading import Thread

#from contextlib import redirect_stdout

#from tensorflow.keras.models import load_model

#from queue import Queue

import subprocess

#def automl(io_stream, out_queue):
	#with redirect_stdout(f):
		#x_to_predict = pd.read_csv("C:/Users/hda10126/Desktop/titanic-dataset/titanic_test.csv", quotechar='"', skipinitialspace=True)
		#x_to_predict_numpy = x_to_predict.to_numpy()
		#clf = ak.StructuredDataClassifier(overwrite=True, max_trials=3, seed=42)
		#clf.fit("C:/Users/hda10126/Desktop/titanic-dataset/titanic_train.csv", "survived", epochs=10)
		#result = clf.predict(x_to_predict_numpy.astype(np.unicode))
		#print(result)
		#model = clf.export_model()
		#model.summary()
		#model.save("model_autokeras", save_format="tf")
		#loaded_model = load_model("model_autokeras", custom_objects=ak.CUSTOM_OBJECTS)
		#loaded_model.summary()
		#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		#for root, dirs, files in os.walk(BASE_DIR, topdown = False):
		#	for name in files:
				#print(os.path.join(root, name))

		#predicted_y = loaded_model.predict(x_to_predict_numpy.astype(np.unicode))
		#predicted_y[predicted_y < 0.5] = 0
		#predicted_y[predicted_y > 0.5] = 1

		#print(predicted_y)
	#print('Got stdout111111111111: "{0}"'.format(f.getvalue()))

if __name__ == '__main__':
	#f = io.StringIO()
	#q = Queue()
	#t1 = Thread(target = automl, args=(f,q,))
	#t1.start()

	process = subprocess.Popen(".\env\Scripts\python.exe AutoML.py", stdout=subprocess.PIPE, universal_newlines=True)
	capture = ""
	s = process.stdout.read(1)
	capture += s
	while len(s) > 0:
		if capture[len(capture)-1] is '\n':
			sys.stdout.write(capture)
			sys.stdout.flush()
			capture = ""
		capture += s
		s = process.stdout.read(1)


	#with redirect_stdout(f):
	#print('Got stdout222222222222: "{0}"'.format(f.getvalue()))