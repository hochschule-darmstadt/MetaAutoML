import json
import os

from AutoMLs.StructuredDataAutoML import StructuredDataAutoML

if __name__ == '__main__':
    """
    Entry point for the AutoML subprocess, read configuration json and execute the correct AutoML task
    """
    json_file = open('gluon-job.json')
    processJson = json.load(json_file)

    if processJson["task"] == 1:
        classificationTask = StructuredDataAutoML(processJson)
        classificationTask.execute_task()
