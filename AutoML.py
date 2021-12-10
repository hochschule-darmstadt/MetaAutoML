import json
from Utils.JsonUtil import get_config_property

from AutoMLs.StructuredDataAutoML import StructuredDataAutoML

if __name__ == '__main__':
    file_path = os.path.join(get_config_property("job-file-path"),
                             get_config_property("job-file-name"))
    with open(file_path) as file:
        process_json = json.load(file)

    structured_data_automl = StructuredDataAutoML(process_json)

    if processJson["task"] == 1:
        # Classification
        structured_data_automl.classification()

