import json
import os
import logging
import sys

from AutoMLs.StructuredDataAutoML import StructuredDataAutoML

if __name__ == '__main__':
	FORMAT = '%(asctime)s %(message)s'
	logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=FORMAT)

	json_file = open('flaml-job.json')
	processJson = json.load(json_file)
	processJson = json.loads(processJson)
	

	if processJson["task"] == 1:
	    #Classification
		classificationTask = StructuredDataAutoML(processJson)
		classificationTask.classification()
