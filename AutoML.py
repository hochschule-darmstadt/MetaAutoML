import json
import os
from Utils.JsonUtil import get_config_property

from AutoMLs.StructuredDataAutoML import StructuredDataAutoML

if __name__ == '__main__':
    """
    Entry point for the AutoML subprocess, read configuration json and execute the correct AutoML task
    """
    file_path = os.path.join(get_config_property("job-file-path"),
                             get_config_property("job-file-name"))
    with open(file_path) as file:
        process_json = json.load(file)

    structuredDataAutoML = StructuredDataAutoML(process_json)

    if process_json["task"] == 1:
        # Classification
        structuredDataAutoML.classification()

    elif process_json["task"] == 2:
        # Regression
        structuredDataAutoML.regression()
