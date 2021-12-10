import json
import os

from AutoMLs.StructuredDataAutoML import StructuredDataAutoML
from Utils.JsonUtil import get_config_property

if __name__ == '__main__':
    file_path = os.path.join(get_config_property("job-file-path"),
                             get_config_property("job-file-name"))
    with open(file_path) as file:
        process_json = json.load(file)

    structuredDataAutoML = StructuredDataAutoML(process_json)

    if process_json["task"] == 1:
        structuredDataAutoML.classification()

    elif process_json["task"] == 2:
        structuredDataAutoML.regression()
