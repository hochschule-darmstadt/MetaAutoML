import json
import os 

from AutoMLs.StructuredDataAutoML import StructuredDataAutoML

if __name__ == '__main__':
	json_file = open('flaml-job.json')
	processJson = json.load(json_file)
	processJson = json.loads(processJson)
	

	if processJson["task"] == 1:
	    #Classification
		classificationTask = StructuredDataAutoML(processJson)
		classificationTask.classification()
