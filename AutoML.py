import json

from AutoMLs.StructuredDataAutoML import StructuredDataAutoML
from Utils.JsonUtil import get_config_property

if __name__ == '__main__':
    json_file = open(get_config_property("job-file-name"))
    processJson = json.load(json_file)
    processJson = json.loads(processJson)
    structuredDataAutoML = StructuredDataAutoML(processJson)

    if processJson["task"] == 1:
        # Classification
        structuredDataAutoML.classification()

    elif processJson["task"] == 2:
        # Regression
        structuredDataAutoML.regression()
